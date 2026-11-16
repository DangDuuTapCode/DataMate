import csv
import hashlib
import sqlite3
import tempfile
import unittest
import xml.sax.saxutils as xml_utils
import zipfile
from pathlib import Path
from unittest.mock import patch

from datamate.ingest import IngestionError, read_business
from datamate.types import SourceLocation


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _column_name(number):
    name = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _cell(reference, value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{reference}"><v>{value}</v></c>'
    text = "" if value is None else xml_utils.escape(str(value))
    return f'<c r="{reference}" t="inlineStr"><is><t>{text}</t></is></c>'


def _write_xlsx(path, sheets, *, date_1904=False, absolute_targets=False):
    sheet_nodes, relation_nodes = [], []
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, sheet in enumerate(sheets, start=1):
            relation_id = f"rId{index}"
            sheet_nodes.append(
                f'<sheet name={xml_utils.quoteattr(sheet["name"])} sheetId="{index}" r:id="{relation_id}"/>'
            )
            target = f"/xl/worksheets/sheet{index}.xml" if absolute_targets else f"worksheets/sheet{index}.xml"
            relation_nodes.append(
                f'<Relationship Id="{relation_id}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                f'Target="{target}"/>'
            )
            rows = []
            for row_number, values in enumerate(sheet["rows"], start=1):
                cells = "".join(
                    _cell(f"{_column_name(column_number)}{row_number}", value)
                    for column_number, value in enumerate(values, start=1)
                )
                rows.append(f'<row r="{row_number}">{cells}</row>')
            sheet_xml = f'<worksheet xmlns="{MAIN_NS}"><sheetData>{"".join(rows)}</sheetData></worksheet>'
            archive.writestr(f"xl/worksheets/sheet{index}.xml", sheet_xml)
        date_properties = '<workbookPr date1904="1"/>' if date_1904 else ""
        workbook = (
            f'<workbook xmlns="{MAIN_NS}" xmlns:r="{REL_NS}">'
            f'{date_properties}'
            f'<sheets>{"".join(sheet_nodes)}</sheets></workbook>'
        )
        relations = (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'{"".join(relation_nodes)}</Relationships>'
        )
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relations)


class CsvIngestionTests(unittest.TestCase):
    def test_header_rows_and_source_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "sales.csv")
            path.write_text("order_id,amount\nA,12.50\nB,3.00\n", encoding="utf-8")
            [table] = read_business(directory)
            self.assertEqual(table.headers, ["order_id", "amount"])
            self.assertEqual(table.rows, [["A", "12.50"], ["B", "3.00"]])
            self.assertEqual(table.source, "sales.csv")
            self.assertEqual(table.row_locations, [
                SourceLocation("sales.csv", "sales", 2),
                SourceLocation("sales.csv", "sales", 3),
            ])

    def test_empty_file_and_header_only_file(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "empty.csv").write_bytes(b"")
            [empty] = read_business(directory)
            self.assertEqual(empty.issues, ["empty_file"])
            self.assertTrue(empty.ingestion_stats.reconciled)
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "header.csv").write_text("id,value\n", encoding="utf-8")
            [table] = read_business(directory)
            self.assertEqual(table.headers, ["id", "value"])
            self.assertEqual(table.rows, [])
            self.assertEqual(table.ingestion_stats.header_rows, 1)
            self.assertTrue(table.ingestion_stats.reconciled)

    def test_blank_and_repeated_headers_are_explicitly_reconciled(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "sales.csv").write_text(
                "id,value\nA,1\n\nid,value\nB,2\n", encoding="utf-8"
            )
            [table] = read_business(directory)
            stats = table.ingestion_stats
            self.assertEqual((stats.source_records, stats.accepted_rows, stats.skipped_rows), (4, 2, 2))
            self.assertEqual(stats.blank_rows_skipped, 1)
            self.assertEqual(stats.repeated_header_rows_skipped, 1)
            self.assertTrue(stats.reconciled)

    def test_malformed_and_ragged_records_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "broken.csv").write_text('a,b\n"unterminated,2\n', encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "malformed CSV"):
                read_business(directory)
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "ragged.csv").write_text("a,b\n1,2\n3\n", encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "expected 2") as caught:
                read_business(directory)
            error = caught.exception
            self.assertEqual(error.code, "row_width_mismatch")
            self.assertEqual((error.stats.source_records, error.stats.accepted_rows, error.stats.rejected_rows), (2, 1, 1))
            self.assertFalse(error.stats.scan_complete)
            self.assertFalse(error.stats.reconciled)

    def test_file_error_collector_keeps_other_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a_broken.csv").write_text('a,b\n"unterminated,2\n', encoding="utf-8")
            Path(directory, "z_good.csv").write_text("id,value\nA,1\n", encoding="utf-8")
            errors = []
            tables = read_business(directory, errors=errors)
            self.assertEqual([table.source for table in tables], ["z_good.csv"])
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].code, "malformed_csv")
            self.assertFalse(errors[0].stats.scan_complete)
            self.assertFalse(errors[0].stats.reconciled)

    def test_blank_and_duplicate_headers_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "blank.csv").write_text(",  \n1,2\n", encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "header"):
                read_business(directory)
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "duplicate.csv").write_text("id,ID\n1,2\n", encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "duplicate"):
                read_business(directory)

    def test_large_csv_rows_and_physical_line_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "large.csv")
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["id", "value"])
                for row_number in range(1, 2501):
                    writer.writerow([row_number, f"v{row_number}"])
            [table] = read_business(directory)
            self.assertEqual(len(table.rows), 2500)
            self.assertEqual(table.rows[-1], ["2500", "v2500"])
            self.assertEqual(table.row_locations[-1], SourceLocation("large.csv", "large", 2501))


class XlsxIngestionTests(unittest.TestCase):
    def test_absolute_relationship_target_and_multiple_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "book.xlsx")
            _write_xlsx(path, [
                {"name": "Sales", "rows": [["Date", "Amount"], ["2026-01-01", 42]]},
                {"name": "Stock", "rows": [["SKU", "Quantity"], ["P1", 4]]},
            ], date_1904=True, absolute_targets=True)
            sales, stock = read_business(directory)
            self.assertEqual((sales.name, stock.name), ("book:Sales", "book:Stock"))
            self.assertEqual(sales.date_system, "1904")
            self.assertEqual(sales.rows, [["2026-01-01", 42]])
            self.assertEqual(sales.row_locations, [SourceLocation("book.xlsx", "book:Sales", 2)])

    def test_blank_and_duplicate_headers_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            _write_xlsx(Path(directory, "blank.xlsx"), [{"name": "Data", "rows": [["Date", ""], [61, 1]]}])
            with self.assertRaisesRegex(IngestionError, "blank header"):
                read_business(directory)
        with tempfile.TemporaryDirectory() as directory:
            _write_xlsx(Path(directory, "duplicate.xlsx"), [{"name": "Data", "rows": [["Amount", "amount"], [1, 2]]}])
            with self.assertRaisesRegex(IngestionError, "duplicate headers"):
                read_business(directory)

    def test_leading_merged_title_rows_are_skipped_before_header(self):
        with tempfile.TemporaryDirectory() as directory:
            _write_xlsx(Path(directory, "merged.xlsx"), [{
                "name": "Data", "rows": [["Sales", ""], ["Date", "Amount"], [61, 100]]
            }])
            [table] = read_business(directory)
            self.assertEqual(table.headers, ["Date", "Amount"])
            self.assertEqual(table.rows, [[61, 100]])
            self.assertEqual(table.row_locations, [SourceLocation("merged.xlsx", "merged:Data", 3)])
            self.assertEqual(table.ingestion_stats.source_records, 2)
            self.assertEqual(table.ingestion_stats.accepted_rows, 1)
            self.assertEqual(table.ingestion_stats.skipped_rows, 1)
            self.assertEqual(table.ingestion_stats.preamble_rows_skipped, 1)
            self.assertTrue(table.ingestion_stats.reconciled)

    def test_blank_preamble_and_repeated_header_rows_are_reconciled(self):
        with tempfile.TemporaryDirectory() as directory:
            _write_xlsx(Path(directory, "report.xlsx"), [{
                "name": "Data",
                "rows": [["Report title", None], [None, None], ["ID", "Value"],
                         ["A", 1], ["ID", "Value"], [None, None]],
            }])
            [table] = read_business(directory)
            stats = table.ingestion_stats
            self.assertEqual((stats.source_records, stats.accepted_rows, stats.skipped_rows), (5, 1, 4))
            self.assertEqual(stats.preamble_rows_skipped, 2)
            self.assertEqual(stats.blank_rows_skipped, 2)
            self.assertEqual(stats.repeated_header_rows_skipped, 1)
            self.assertTrue(stats.reconciled)

    def test_malformed_xlsx_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "broken.xlsx").write_bytes(b"not an xlsx")
            with self.assertRaisesRegex(IngestionError, "cannot read XLSX"):
                read_business(directory)


class SqliteIngestionTests(unittest.TestCase):
    def test_reader_uses_read_only_connection_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "sales.sqlite")
            connection = sqlite3.connect(path)
            connection.execute('CREATE TABLE "sales" ("order id" TEXT, amount INTEGER)')
            connection.execute('INSERT INTO "sales" VALUES (?, ?)', ("A", 42))
            connection.commit()
            connection.close()
            before = hashlib.sha256(path.read_bytes()).digest()
            with patch("datamate.ingest.sqlite3.connect", wraps=sqlite3.connect) as connect:
                [table] = read_business(directory)
                self.assertIn("?mode=ro", connect.call_args.args[0])
            self.assertEqual(table.headers, ["order id", "amount"])
            self.assertEqual(table.rows, [["A", 42]])
            self.assertEqual(table.row_locations, [SourceLocation("sales.sqlite", "sales", 1)])
            self.assertEqual(table.ingestion_stats.source_records, 1)
            self.assertEqual(table.ingestion_stats.accepted_rows, 1)
            self.assertTrue(table.ingestion_stats.reconciled)
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)


if __name__ == "__main__":
    unittest.main()
