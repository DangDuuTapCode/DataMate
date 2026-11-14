"""Read CSV/XLSX/SQLite without mutating the mounted competition data."""
import csv
import json
import posixpath
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from .types import Question, SourceLocation, Table

NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class IngestionError(ValueError):
    """An input cannot be read without guessing or losing structure."""

    def __init__(self, path, message):
        self.path = Path(path)
        super().__init__(f"{self.path.name}: {message}")


def _column(ref):
    return "".join(c for c in (ref or "") if c.isalpha())


def _csv(path):
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as handle:
                reader = csv.reader(handle, strict=True)
                try:
                    headers = next(reader)
                except StopIteration:
                    return []
                if not headers or not any(str(value).strip() for value in headers):
                    raise IngestionError(path, "CSV has no usable header row")
                rows, locations = [], []
                for row in reader:
                    if not row or not any(str(value).strip() for value in row):
                        continue
                    if len(row) != len(headers):
                        raise IngestionError(
                            path,
                            f"row ending at line {reader.line_num} has {len(row)} fields; expected {len(headers)}",
                        )
                    rows.append(row)
                    locations.append(SourceLocation(path.name, path.stem, reader.line_num))
            break
        except UnicodeDecodeError:
            continue
        except csv.Error as error:
            raise IngestionError(path, f"malformed CSV at line {reader.line_num}: {error}") from error
    else:
        raise IngestionError(path, "could not decode CSV with supported encodings")
    return [Table(path.stem, headers, rows, path.name, row_locations=locations)]


def _xlsx(path):
    """Read XLSX sheets one XML row at a time while retaining raw cell values.

    This reader intentionally rejects incomplete or multi-row headers. Choosing
    how to merge such headers is business-specific, so silently guessing would
    create a corrupted schema for a later planner or executor.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            shared = []
            if "xl/sharedStrings.xml" in archive.namelist():
                root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
                shared = ["".join(item.itertext()) for item in root.findall("x:si", NS)]
            book = ET.fromstring(archive.read("xl/workbook.xml"))
            relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            rels = {item.attrib["Id"]: item.attrib["Target"] for item in relations}
            relation_key = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            properties = book.find("x:workbookPr", NS)
            date_system = "1904" if properties is not None and properties.attrib.get("date1904") in ("1", "true", "True") else "1900"
            for sheet in book.findall("x:sheets/x:sheet", NS):
                target = rels.get(sheet.attrib.get(relation_key), "")
                member = posixpath.normpath(target if target.startswith("xl/") else "xl/" + target)
                if member not in archive.namelist():
                    raise IngestionError(path, f"worksheet target is missing: {target!r}")
                sheet_name = sheet.attrib.get("name", "Sheet")
                table_name = f"{path.stem}:{sheet_name}"
                headers, columns, rows, locations = None, (), [], []
                with archive.open(member) as stream:
                    for _, row in ET.iterparse(stream, events=("end",)):
                        if not row.tag.endswith("}row"):
                            continue
                        values = {}
                        for cell in row.findall("x:c", NS):
                            raw = cell.findtext("x:v", default="", namespaces=NS)
                            inline = cell.find("x:is", NS)
                            if inline is not None:
                                raw = "".join(inline.itertext())
                            elif cell.attrib.get("t") == "s" and raw:
                                raw = shared[int(raw)]
                            elif cell.attrib.get("t") not in ("str", "inlineStr") and raw:
                                try:
                                    number = float(raw)
                                    raw = int(number) if number.is_integer() else number
                                except ValueError:
                                    pass
                            values[_column(cell.attrib.get("r"))] = raw
                        row_number = int(row.attrib.get("r", "0")) or None
                        if headers is None:
                            if not values:
                                row.clear()
                                continue
                            columns = tuple(sorted(values, key=lambda key: (len(key), key)))
                            headers = [str(values.get(column, "")).strip() for column in columns]
                            if any(not header for header in headers):
                                raise IngestionError(path, f"worksheet {sheet_name!r} has blank header cells at row {row_number}")
                            if len({header.casefold() for header in headers}) != len(headers):
                                raise IngestionError(path, f"worksheet {sheet_name!r} has duplicate headers at row {row_number}")
                        elif any(values.get(column, "") != "" for column in columns) or values:
                            unexpected = sorted(set(values).difference(columns))
                            if unexpected:
                                raise IngestionError(
                                    path,
                                    f"worksheet {sheet_name!r} row {row_number} adds columns {unexpected}; "
                                    "configure its multi-row or merged header explicitly",
                                )
                            rows.append([values.get(column, "") for column in columns])
                            locations.append(SourceLocation(path.name, table_name, row_number))
                        row.clear()
                if headers:
                    yield Table(table_name, headers, rows, path.name, row_locations=locations, date_system=date_system)
    except (ET.ParseError, OSError, zipfile.BadZipFile, KeyError, ValueError) as error:
        if isinstance(error, IngestionError):
            raise
        raise IngestionError(path, f"cannot read XLSX: {error}") from error


def _sqlite(path):
    try:
        connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    except sqlite3.Error as error:
        raise IngestionError(path, f"cannot open SQLite read-only: {error}") from error
    try:
        names = [r[0] for r in connection.execute("select name from sqlite_master where type='table' order by name")]
        for name in names:
            escaped = name.replace('"', '""')
            cursor = connection.execute(f'select * from "{escaped}"')
            rows, locations = [], []
            for row_number, row in enumerate(cursor, start=1):
                rows.append(list(row))
                locations.append(SourceLocation(path.name, name, row_number))
            yield Table(name, [d[0] for d in cursor.description], rows, path.name, row_locations=locations)
    except sqlite3.Error as error:
        raise IngestionError(path, f"cannot read SQLite: {error}") from error
    finally:
        connection.close()


def read_business(directory):
    tables = []
    for path in sorted(Path(directory).iterdir(), key=lambda x: x.name.casefold()):
        if path.suffix.lower() == ".csv":
            tables.extend(_csv(path))
        elif path.suffix.lower() == ".xlsx":
            tables.extend(_xlsx(path))
        elif path.suffix.lower() in (".sqlite", ".sqlite3", ".db"):
            tables.extend(_sqlite(path))
    return tables


def read_questions(path):
    with open(path, encoding="utf-8") as handle:
        return [Question(**json.loads(line)) for line in handle if line.strip()]


def profile(tables):
    return [{"name": t.name, "source": t.source, "rows": len(t.rows), "columns": t.headers,
             "date_system": t.date_system, "issues": list(t.issues)} for t in tables]
