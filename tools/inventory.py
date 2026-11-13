#!/usr/bin/env python3
"""inventory.py - Kiểm kê một split DataMate (train / public_test).

Chạy:   python inventory.py <thư_mục_split> <file_json_ra> [--titles]
Vào:    <split>/data/<biz>/*.csv | *.xlsx | *.sqlite  +  README.md
Ra:     1 file JSON (mỗi business: file, bảng/sheet, cột, số dòng, độ dài README)
        và bảng tóm tắt in ra màn hình.
Chỉ ĐỌC dữ liệu, không sửa. Đọc nhẹ (header + vài dòng) để chạy nhanh với file lớn.
"""
import csv
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from statistics import median

ENCODINGS = ("utf-8-sig", "utf-8", "cp1258", "latin-1")


def csv_info(path, head=2):
    for enc in ENCODINGS:
        try:
            with open(path, newline="", encoding=enc) as f:
                rows = []
                for i, r in enumerate(csv.reader(f)):
                    rows.append(r)
                    if i >= head:
                        break
                n = len(rows)
                for _ in f:  # đếm phần còn lại, không parse
                    n += 1
            return {"kind": "csv", "encoding": enc, "rows": max(n - 1, 0),
                    "cols": rows[0] if rows else [], "head": rows[1:]}
        except UnicodeDecodeError:
            continue
    return {"kind": "csv", "error": "encoding"}


def xlsx_info(path, head=2):
    """Đọc nhẹ: header + vài dòng; số dòng lấy từ thẻ <dimension> (nhanh), -1 nếu file không có thẻ này."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = []
    for ws in wb.worksheets:
        rows = []
        for r in ws.iter_rows(values_only=True):
            rows.append([None if v is None else str(v)[:40] for v in r])
            if len(rows) > head:
                break
        mr = ws.max_row
        sheets.append({"sheet": ws.title, "rows": (mr - 1) if mr else -1,
                       "cols": rows[0] if rows else [], "head": rows[1:]})
    wb.close()
    return {"kind": "xlsx", "sheets": sheets}


def sqlite_info(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = con.cursor()
    out = []
    q = "select name, type from sqlite_master where type in ('table','view') and name not like 'sqlite_%'"
    for name, typ in cur.execute(q).fetchall():
        cols = [r[1] for r in cur.execute(f'pragma table_info("{name}")')]
        n = cur.execute(f'select count(*) from "{name}"').fetchone()[0]
        out.append({"table": name, "type": typ, "rows": n, "cols": cols})
    con.close()
    return {"kind": "sqlite", "tables": out}


def scan(split_dir):
    res = {"businesses": {}}
    for bdir in sorted((Path(split_dir) / "data").iterdir()):
        if not bdir.is_dir():
            continue
        info = {"files": {}, "readme_chars": 0, "readme_title": ""}
        for p in sorted(bdir.iterdir()):
            if p.name.lower() == "readme.md":
                txt = p.read_text(encoding="utf-8", errors="replace")
                info["readme_chars"] = len(txt)
                info["readme_title"] = next((l.strip() for l in txt.splitlines() if l.strip()), "")[:90]
                continue
            ext = p.suffix.lower()
            try:
                if ext == ".csv":
                    d = csv_info(p)
                elif ext in (".xlsx", ".xlsm"):
                    d = xlsx_info(p)
                elif ext in (".sqlite", ".db", ".sqlite3"):
                    d = sqlite_info(p)
                else:
                    d = {"kind": ext or "?"}
            except Exception as e:  # file hỏng không được làm dừng cả quá trình
                d = {"kind": ext, "error": repr(e)[:200]}
            d["bytes"] = p.stat().st_size
            info["files"][p.name] = d
        res["businesses"][bdir.name] = info
    return res


def tables_of(info):
    """Trả về list (tên_bảng, số_dòng, cột) cho mọi bảng/sheet của 1 business."""
    out = []
    for fname, d in info["files"].items():
        stem = Path(fname).stem
        if d.get("kind") == "csv" and "error" not in d:
            out.append((stem, d["rows"], d["cols"]))
        elif d.get("kind") == "xlsx":
            out += [(f"{stem}::{s['sheet']}", s["rows"], s["cols"]) for s in d["sheets"]]
        elif d.get("kind") == "sqlite":
            out += [(f"{stem}::{t['table']}", t["rows"], t["cols"]) for t in d["tables"]]
    return out


def mm(xs):
    xs = sorted(xs)
    return f"min={xs[0]} med={median(xs)} max={xs[-1]}" if xs else "n/a"


def summarize(res, titles=False):
    B = res["businesses"]
    kinds, tabs, rows, mb, readme = Counter(), [], [], [], []
    tnames, cnames = Counter(), Counter()
    for info in B.values():
        ts = tables_of(info)
        kinds.update(d.get("kind") for d in info["files"].values())
        tabs.append(len(ts))
        rows.append(max([t[1] for t in ts] or [0]))
        mb.append(round(sum(d["bytes"] for d in info["files"].values()) / 1e6, 1))
        readme.append(info["readme_chars"])
        for name, _, cols in ts:
            tnames[name.split("::")[-1].lower()] += 1
            cnames.update(str(c).strip().lower() for c in cols)
    print(f"businesses={len(B)} file_kinds={dict(kinds)}")
    print("tables/biz   ", mm(tabs))
    print("max_rows/biz ", mm(rows), "(-1 = xlsx lớn, chưa đếm)")
    print("size_MB/biz  ", mm(mb))
    print("readme_chars ", mm(readme))
    print("top tables :", tnames.most_common(25))
    print("top columns:", cnames.most_common(45))
    if titles:
        for b, info in B.items():
            print(f"{b} | readme={info['readme_chars']:5d} | {info['readme_title']}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    result = scan(sys.argv[1])
    json.dump(result, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
    summarize(result, titles="--titles" in sys.argv)
