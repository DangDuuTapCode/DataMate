"""Read CSV/XLSX/SQLite without mutating the mounted competition data."""
import csv
import json
import posixpath
import re
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from .types import IngestionStats, Question, SourceLocation, Table

NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class IngestionError(ValueError):
    """An input cannot be read without guessing or losing structure."""

    def __init__(self, path, message, *, code="invalid_input", stats=None):
        self.path = Path(path)
        self.code = code
        self.stats = stats or IngestionStats()
        self.stats.scan_complete = False
        super().__init__(f"{self.path.name}: {message}")


def _column(ref):
    return "".join(c for c in (ref or "") if c.isalpha())


def _validate_headers(path, headers, *, source):
    if not headers or not any(str(value).strip() for value in headers):
        raise IngestionError(path, f"{source} has no usable header row", code="missing_header")
    normalized = [str(value).strip().casefold() for value in headers]
    if any(not value for value in normalized):
        raise IngestionError(path, f"{source} has blank header cells", code="blank_header")
    if len(set(normalized)) != len(normalized):
        raise IngestionError(path, f"{source} has duplicate headers", code="duplicate_header")


def _xlsx_rows(stream, shared):
    """Yield worksheet rows while removing completed XML nodes from memory."""
    stack = []
    for event, element in ET.iterparse(stream, events=("start", "end")):
        if event == "start":
            stack.append(element)
            continue
        if element.tag.endswith("}row"):
            values = {}
            for cell in element.findall("x:c", NS):
                raw = cell.findtext("x:v", default="", namespaces=NS)
                inline = cell.find("x:is", NS)
                if inline is not None:
                    raw = "".join(inline.itertext())
                elif cell.attrib.get("t") == "s" and raw:
                    shared_index = int(raw)
                    if shared_index < 0 or shared_index >= len(shared):
                        raise ValueError(f"shared string index is out of range: {shared_index}")
                    raw = shared[shared_index]
                elif cell.attrib.get("t") not in ("str", "inlineStr") and raw:
                    try:
                        number = float(raw)
                        raw = int(number) if number.is_integer() else number
                    except ValueError:
                        pass
                values[_column(cell.attrib.get("r"))] = raw
            row_number = int(element.attrib.get("r", "0")) or None
            yield row_number, values
            if len(stack) > 1:
                stack[-2].remove(element)
            element.clear()
        if stack:
            stack.pop()


def _csv(path):
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        stats = IngestionStats()
        try:
            with open(path, encoding=encoding, newline="") as handle:
                reader = csv.reader(handle, strict=True)
                try:
                    headers = next(reader)
                except StopIteration:
                    return [Table(path.stem, [], [], path.name, issues=["empty_file"], ingestion_stats=stats)]
                _validate_headers(path, headers, source="CSV")
                stats.header_rows = 1
                header_key = tuple(str(value).strip().casefold() for value in headers)
                rows, locations = [], []
                for row in reader:
                    stats.source_records += 1
                    if not row or not any(str(value).strip() for value in row):
                        stats.skipped_rows += 1
                        stats.blank_rows_skipped += 1
                        continue
                    if len(row) != len(headers):
                        stats.rejected_rows += 1
                        raise IngestionError(
                            path,
                            f"row ending at line {reader.line_num} has {len(row)} fields; expected {len(headers)}",
                            code="row_width_mismatch",
                            stats=stats,
                        )
                    if tuple(str(value).strip().casefold() for value in row) == header_key:
                        stats.skipped_rows += 1
                        stats.repeated_header_rows_skipped += 1
                        continue
                    rows.append(row)
                    locations.append(SourceLocation(path.name, path.stem, reader.line_num))
                    stats.accepted_rows += 1
            break
        except UnicodeDecodeError:
            continue
        except csv.Error as error:
            stats.source_records += 1
            stats.rejected_rows += 1
            raise IngestionError(path, f"malformed CSV at line {reader.line_num}: {error}",
                                 code="malformed_csv", stats=stats) from error
    else:
        raise IngestionError(path, "could not decode CSV with supported encodings", code="unsupported_encoding")
    return [Table(
        path.stem, headers, rows, path.name, row_locations=locations,
        ingestion_stats=stats, header_rows=(tuple(headers),), header_row_numbers=(1,),
    )]


def _column_number(name):
    number = 0
    for character in name:
        number = number * 26 + ord(character.upper()) - 64
    return number


def _xlsx_merge_ranges(stream):
    """Read merge references without retaining worksheet row payloads."""
    ranges = []
    stack = []
    for event, element in ET.iterparse(stream, events=("start", "end")):
        if event == "start":
            stack.append(element)
            continue
        if element.tag.endswith("}mergeCell"):
            reference = element.attrib.get("ref")
            if reference:
                ranges.append(reference)
        if element.tag.endswith("}row"):
            if len(stack) > 1:
                stack[-2].remove(element)
            element.clear()
        if stack:
            stack.pop()
    return ranges


def _multirow_header(preamble, merge_ranges):
    """Return a conservative two-row grouped header, or None when uncertain.

    Only horizontal merged groups on one row are considered. At least two
    distinct groups must be present; a single merged report title is not a
    grouped header and is deliberately ignored.
    """
    for index in range(len(preamble) - 1):
        group_row_number, group_values = preamble[index]
        leaf_row_number, leaf_values = preamble[index + 1]
        if leaf_row_number != group_row_number + 1:
            continue
        if not leaf_values or not all(
            isinstance(value, str) and value.strip()
            for value in leaf_values.values()
        ):
            continue

        columns = sorted(leaf_values, key=_column_number)
        groups = []
        for reference in merge_ranges:
            match = re.fullmatch(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", reference.upper())
            if not match:
                continue
            first_col, first_row, last_col, last_row = match.groups()
            if int(first_row) != group_row_number or int(last_row) != group_row_number:
                continue
            first_index, last_index = _column_number(first_col), _column_number(last_col)
            if last_index <= first_index:
                continue
            group_label = group_values.get(first_col, "")
            if not isinstance(group_label, str) or not group_label.strip():
                continue
            covered = [
                column for column in columns
                if first_index <= _column_number(column) <= last_index
            ]
            if len(covered) < 2 or len(covered) != last_index - first_index + 1:
                continue
            groups.append((first_col, first_index, last_index, group_label.strip()))

        if len({group[3] for group in groups}) < 2:
            continue

        group_starts = {group[0] for group in groups}
        nonempty_group_cells = {
            column for column, value in group_values.items()
            if str(value).strip()
        }
        if not nonempty_group_cells.issubset(group_starts):
            continue

        expanded_groups = {}
        for _, first_index, last_index, label in groups:
            for column in columns:
                column_index = _column_number(column)
                if first_index <= column_index <= last_index:
                    expanded_groups[column] = label

        headers = [
            f"{expanded_groups[column]} / {leaf_values[column].strip()}"
            if column in expanded_groups
            else leaf_values[column].strip()
            for column in columns
        ]
        normalized = [header.casefold() for header in headers]
        if len(set(normalized)) != len(normalized):
            continue

        raw_header_rows = (
            tuple(str(group_values.get(column, "")) for column in columns),
            tuple(str(leaf_values.get(column, "")) for column in columns),
        )
        return {
            "start_index": index,
            "end_index": index + 1,
            "row_numbers": (group_row_number, leaf_row_number),
            "columns": columns,
            "headers": headers,
            "raw_rows": raw_header_rows,
        }
    return None


def _xlsx(path):
    """Read XLSX sheets one XML row at a time while retaining raw cell values.

    Leading report titles, filter rows, and blank rows are skipped by selecting
    a conservative two-row merged-header pattern when explicit grouped ranges
    are present, otherwise the widest complete text row among the first 32 rows.
    Ambiguous grouped layouts are not reconstructed.
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
                if target.startswith("/"):
                    member = posixpath.normpath(target.lstrip("/"))
                elif target.startswith("xl/"):
                    member = posixpath.normpath(target)
                else:
                    member = posixpath.normpath(posixpath.join("xl", target))
                if member.startswith("../") or member in ("", ".", "..") or member.startswith("/"):
                    raise IngestionError(path, f"worksheet target escapes workbook package: {target!r}",
                                         code="unsafe_worksheet_target")
                if member not in archive.namelist():
                    raise IngestionError(path, f"worksheet target is missing: {target!r}",
                                         code="missing_worksheet")
                sheet_name = sheet.attrib.get("name", "Sheet")
                table_name = f"{path.stem}:{sheet_name}"
                rows, locations = [], []
                stats = IngestionStats()
                with archive.open(member) as merge_stream:
                    merge_ranges = _xlsx_merge_ranges(merge_stream)
                with archive.open(member) as stream:
                    row_iterator = iter(_xlsx_rows(stream, shared))
                    preamble_all = []
                    for _ in range(32):
                        try:
                            row_number, values = next(row_iterator)
                        except StopIteration:
                            break
                        preamble_all.append((row_number, values))
                    preamble = [(number, values) for number, values in preamble_all if values]
                    if not preamble:
                        stats.source_records = len(preamble_all)
                        stats.skipped_rows = stats.source_records
                        stats.blank_rows_skipped = stats.source_records
                        yield Table(table_name, [], [], path.name, issues=["empty_sheet"],
                                    date_system=date_system, ingestion_stats=stats)
                        continue

                    multi_header = _multirow_header(preamble, merge_ranges)
                    if multi_header is not None:
                        header_start_index = next(
                            index for index, (number, _) in enumerate(preamble_all)
                            if number == multi_header["row_numbers"][0]
                        )
                        header_end_index = next(
                            index for index, (number, _) in enumerate(preamble_all)
                            if number == multi_header["row_numbers"][1]
                        )
                        columns = multi_header["columns"]
                        headers = multi_header["headers"]
                        raw_header_rows = multi_header["raw_rows"]
                        header_row_numbers = multi_header["row_numbers"]
                    else:
                        candidates = [
                            index for index, (_, values) in enumerate(preamble)
                            if values and all(isinstance(value, str) and value.strip() for value in values.values())
                        ]
                        if not candidates:
                            potential = [
                                index for index, (_, values) in enumerate(preamble)
                                if values and all(isinstance(value, str) for value in values.values())
                            ]
                            if potential:
                                widest = max(len(preamble[index][1]) for index in potential)
                                index = next(index for index in potential if len(preamble[index][1]) == widest)
                                row_number, values = preamble[index]
                                columns = tuple(sorted(values, key=_column_number))
                                _validate_headers(
                                    path,
                                    [str(values.get(column, "")).strip() for column in columns],
                                    source=f"worksheet {sheet_name!r} at row {row_number}",
                                )
                            raise IngestionError(
                                path,
                                f"worksheet {sheet_name!r} has no complete text header in its first 32 rows",
                                code="missing_header",
                                stats=stats,
                            )
                        width = max(len(preamble[index][1]) for index in candidates)
                        header_index = next(index for index in candidates if len(preamble[index][1]) == width)
                        header_row, header_values = preamble[header_index]
                        columns = tuple(sorted(header_values, key=_column_number))
                        headers = [str(header_values.get(column, "")).strip() for column in columns]
                        _validate_headers(path, headers, source=f"worksheet {sheet_name!r} at row {header_row}")
                        raw_header_rows = (tuple(headers),)
                        header_row_numbers = (header_row,)
                        header_start_index = next(
                            index for index, (number, _) in enumerate(preamble_all) if number == header_row
                        )
                        header_end_index = header_start_index

                    _validate_headers(path, headers, source=f"worksheet {sheet_name!r} at rows {header_row_numbers}")
                    header_key = tuple(header.casefold() for header in headers)
                    stats.header_rows = len(header_row_numbers)

                    for _, values in preamble_all[:header_start_index]:
                        stats.source_records += 1
                        stats.skipped_rows += 1
                        stats.preamble_rows_skipped += 1
                        if not values or not any(str(value).strip() for value in values.values()):
                            stats.blank_rows_skipped += 1

                    def retain_row(row_number, values):
                        stats.source_records += 1
                        if not values or not any(str(value).strip() for value in values.values()):
                            stats.skipped_rows += 1
                            stats.blank_rows_skipped += 1
                            return
                        row_key = tuple(str(values.get(column, "")).strip().casefold() for column in columns)
                        if row_key == header_key:
                            stats.skipped_rows += 1
                            stats.repeated_header_rows_skipped += 1
                            return
                        unexpected = sorted(
                            column for column, value in values.items()
                            if column not in columns and str(value).strip()
                        )
                        if unexpected:
                            raise IngestionError(
                                path,
                                f"worksheet {sheet_name!r} row {row_number} adds populated columns {unexpected}",
                                code="unexpected_populated_column",
                                stats=stats,
                            )
                        rows.append([values.get(column, "") for column in columns])
                        locations.append(SourceLocation(path.name, table_name, row_number))
                        stats.accepted_rows += 1

                    for row_number, values in preamble_all[header_end_index + 1:]:
                        retain_row(row_number, values)
                    for row_number, values in row_iterator:
                        retain_row(row_number, values)
                if headers:
                    yield Table(
                        table_name, headers, rows, path.name,
                        row_locations=locations, date_system=date_system,
                        ingestion_stats=stats, header_rows=raw_header_rows,
                        header_row_numbers=header_row_numbers,
                    )
    except (ET.ParseError, OSError, zipfile.BadZipFile, KeyError, ValueError) as error:
        if isinstance(error, IngestionError):
            raise
        raise IngestionError(path, f"cannot read XLSX: {error}", code="invalid_xlsx") from error


def _sqlite(path):
    try:
        connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    except sqlite3.Error as error:
        raise IngestionError(path, f"cannot open SQLite read-only: {error}", code="sqlite_open") from error
    try:
        names = [r[0] for r in connection.execute("select name from sqlite_master where type='table' order by name")]
        for name in names:
            escaped = name.replace('"', '""')
            cursor = connection.execute(f'select * from "{escaped}"')
            rows, locations = [], []
            stats = IngestionStats()
            for row_number, row in enumerate(cursor, start=1):
                rows.append(list(row))
                locations.append(SourceLocation(path.name, name, row_number))
                stats.source_records += 1
                stats.accepted_rows += 1
            yield Table(name, [d[0] for d in cursor.description], rows, path.name,
                        row_locations=locations, ingestion_stats=stats)
    except sqlite3.Error as error:
        raise IngestionError(path, f"cannot read SQLite: {error}", code="sqlite_read") from error
    finally:
        connection.close()


def read_business(directory, *, errors=None):
    """Read one business; optionally collect file errors and continue other files.

    With no error collector, existing fail-fast behavior is preserved.
    """
    tables = []
    for path in sorted(Path(directory).iterdir(), key=lambda x: x.name.casefold()):
        try:
            if path.suffix.lower() == ".csv":
                tables.extend(_csv(path))
            elif path.suffix.lower() == ".xlsx":
                tables.extend(_xlsx(path))
            elif path.suffix.lower() in (".sqlite", ".sqlite3", ".db"):
                tables.extend(_sqlite(path))
        except IngestionError as error:
            if errors is None:
                raise
            errors.append(error)
    return tables


def read_questions(path):
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("question record must be a JSON object")
                yield Question(**record)
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                raise ValueError(f"invalid question JSONL record at line {line_number}: {error}") from error


def profile(tables):
    return [{"name": t.name, "source": t.source, "rows": len(t.rows), "columns": t.headers,
             "date_system": t.date_system, "issues": list(t.issues),
             "ingestion_stats": vars(t.ingestion_stats),
             "reconciled": t.ingestion_stats.reconciled} for t in tables]
