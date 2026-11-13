#!/usr/bin/env python3
"""qstats.py - Thống kê câu hỏi / đáp án của một split DataMate.

Chạy:   python qstats.py <thư_mục_split> [số_mẫu=40]
Vào:    <split>/questions.jsonl, <split>/answers.jsonl (chỉ có ở train)
In ra:  kiểu đáp án, tỉ lệ unanswerable, họ câu hỏi (regex - INFERRED), biểu thức thời gian,
        mức nhiễu ngôn ngữ (không dấu, viết tắt) và mẫu ngẫu nhiên (seed cố định = 7).
Lưu ý:  regex chỉ để THỐNG KÊ/phân loại sơ bộ, không dùng để trả lời câu hỏi.
"""
import json
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def fold(s):
    """Bỏ dấu + lower - chỉ để NHẬN DIỆN, không dùng để so khớp đáp án."""
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


FAMILY = {  # regex trên chuỗi đã fold; đoán ban đầu, tinh chỉnh sau khi đọc mẫu
    "doanh_thu": r"doanh thu|doanh so|\bdt\b|thu ve|ban duoc bao nhieu tien|tien hang",
    "loi_nhuan_gia_von": r"loi nhuan|\blai\b|\blo\b|gia von|bien loi",
    "so_luong_ban": r"ban duoc bao nhieu|so luong ban|ban ra",
    "xep_hang": r"nhat|\btop\b|it nhat|cham nhat|xep hang",
    "ton_kho": r"ton kho|\bton\b|con bao nhieu|het hang|sap het|ton cuoi",
    "han_dung_lo": r"het han|han dung|\bdate\b|hsd|\blo\b",
    "cong_no": r"\bno\b|cong no|chua tra|chua thanh toan|con no",
    "so_sanh": r"so voi|cung ky|tang|giam|chenh lech|%|phan tram|ti le|ty le",
    "huy_tra_hoan": r"huy|hoan|tra hang|tra lai",
    "khach_hang": r"khach|\bkh\b",
    "nhan_vien_ca": r"nhan vien|\bnv\b|luong|ca lam|cham cong",
    "nhap_hang_ncc": r"nhap hang|mua vao|nha cung cap|\bncc\b|don nhap",
    "ngay_le_tet": r"\btet\b|trung thu|30/4|quoc khanh|noel|valentine|8/3|20/10",
    "dem_don": r"bao nhieu don|so don|dem don|may don",
    "gia": r"gia ban|gia nhap|don gia|\bgia\b",
    "ngay_cu_the": r"ngay nao|hom nao|thu may|khi nao",
}
TIME = {
    "hom_nay_qua": r"hom nay|hom qua|bua qua",
    "tuan": r"\btuan\b",
    "thang_nay": r"thang nay",
    "thang_truoc": r"thang (roi|truoc|vua roi)",
    "quy": r"\bquy\b|\bq[1-4]\b",
    "nam": r"\bnam\b",
    "cung_ky": r"cung ky",
    "n_ngay_qua": r"\d+ ngay (qua|gan day|truoc)|ngay qua",
    "thang_so": r"thang \d{1,2}",
    "ngay_so": r"\d{1,2}/\d{1,2}|ngay \d{1,2}",
    "tet": r"\btet\b",
    "dau_cuoi": r"dau thang|cuoi thang|dau nam|cuoi nam|cuoi tuan",
}
ABBR = r"\b(ko|k|dc|dk|sp|kh|nv|ncc|dt|ln|ntn|bn|bnhieu|j|vs|hk|hok|thg)\b"


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "n/a"


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    split = Path(sys.argv[1])
    nsample = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    Q = load(split / "questions.jsonl")
    ap = split / "answers.jsonl"
    A = {a["id"]: a for a in load(ap)} if ap.exists() else {}
    n = len(Q)
    per = Counter(q["business_id"] for q in Q)
    print(f"questions={n} businesses={len(per)} answers={len(A)} | q/biz min {min(per.values())} "
          f"med {median(per.values())} max {max(per.values())}")
    dates = sorted(q["as_of_date"] for q in Q)
    print("as_of_date:", dates[0], "->", dates[-1], "| distinct", len(set(dates)))
    print("words/question: med", median(len(q["question"].split()) for q in Q),
          "max", max(len(q["question"].split()) for q in Q))
    F = [fold(q["question"]) for q in Q]
    nodiac = sum(1 for q, f in zip(Q, F) if q["question"].lower().replace("đ", "d") == f)
    print("không dấu:", pct(nodiac, n), "| viết tắt:", pct(sum(1 for f in F if re.search(ABBR, f)), n))
    print("HỌ (chồng nhau):", {k: pct(sum(1 for f in F if re.search(v, f)), n) for k, v in FAMILY.items()})
    print("THỜI GIAN:", {k: pct(sum(1 for f in F if re.search(v, f)), n) for k, v in TIME.items()})
    if A:
        T = Counter(A[q["id"]]["type"] for q in Q if q["id"] in A)
        print("KIỂU ĐÁP ÁN:", {k: f"{v} ({pct(v, n)})" for k, v in T.most_common()})
        byfam = defaultdict(Counter)
        for q, f in zip(Q, F):
            for k, v in FAMILY.items():
                if re.search(v, f) and q["id"] in A:
                    byfam[k][A[q["id"]]["type"]] += 1
        for k, c in byfam.items():
            print(f"  {k:18s}", dict(c.most_common()))
        un = defaultdict(lambda: [0, 0])
        for q in Q:
            a = A.get(q["id"])
            if a:
                un[q["business_id"]][1] += 1
                un[q["business_id"]][0] += a["type"] == "unanswerable"
        r = sorted(u / t for u, t in un.values())
        print("unanswerable/biz: min %.2f med %.2f max %.2f" % (r[0], median(r), r[-1]))
        nums = [num(a["answer"]) for a in A.values() if a["type"] == "number"]
        nums = [x for x in nums if x is not None]
        print("number: nguyên", sum(x.is_integer() for x in nums), "/", len(nums), "| âm", sum(x < 0 for x in nums))
        print("list len:", sorted(Counter(len(a["answer"]) for a in A.values() if a["type"] == "list").items()))
        print("table (rows,cols):", Counter((len(a["answer"]["rows"]), len(a["answer"]["columns"]))
                                            for a in A.values() if a["type"] == "table").most_common(8))
        s = [a for a in A.values() if a["type"] == "string"]
        print("string có alias:", sum(1 for a in s if a.get("alias")), "/", len(s))
    random.seed(7)
    for q in random.sample(Q, min(nsample, n)):
        a = A.get(q["id"])
        tail = f" -> [{a['type']}] {json.dumps(a.get('answer'), ensure_ascii=False)[:70]}" if a else ""
        print(f"{q['business_id']} {q['as_of_date']} | {q['question']}{tail}")


if __name__ == "__main__":
    main()
