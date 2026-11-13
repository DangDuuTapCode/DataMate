"""Read CSV/XLSX/SQLite without mutating the mounted competition data."""
import csv
import json
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from .types import Question, Table

NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _column(ref):
    return "".join(c for c in (ref or "") if c.isalpha())


def _csv(path):
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as handle:
                data = list(csv.reader(handle))
            break
        except UnicodeDecodeError:
            continue
    else:
        return []
    if not data:
        return []
    width = len(data[0])
    return [Table(path.stem, data[0], [r + [""] * (width - len(r)) for r in data[1:] if any(r)], path.name)]


def _xlsx(path):
    """Streaming XML reader; keeps memory bounded by one sheet row."""
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(x.itertext()) for x in root.findall("x:si", NS)]
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rels = {x.attrib["Id"]: x.attrib["Target"] for x in relations}
        relation_key = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        for sheet in book.findall("x:sheets/x:sheet", NS):
            target = rels.get(sheet.attrib.get(relation_key), "")
            member = target if target.startswith("xl/") else "xl/" + target
            if member not in archive.namelist():
                continue
            headers, columns, rows = None, (), []
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
                    if headers is None:
                        columns = tuple(sorted(values, key=lambda x: (len(x), x)))
                        headers = [str(values.get(c, "")).strip() or c for c in columns]
                    elif any(values.get(c, "") != "" for c in columns):
                        rows.append([values.get(c, "") for c in columns])
                    row.clear()
            if headers:
                yield Table(f"{path.stem}:{sheet.attrib.get('name', 'Sheet')}", headers, rows, path.name)


def _sqlite(path):
    connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    try:
        names = [r[0] for r in connection.execute("select name from sqlite_master where type='table' order by name")]
        for name in names:
            escaped = name.replace('"', '""')
            cursor = connection.execute(f'select * from "{escaped}"')
            yield Table(name, [d[0] for d in cursor.description], [list(r) for r in cursor], path.name)
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
    return [{"name": t.name, "source": t.source, "rows": len(t.rows), "columns": t.headers} for t in tables]
