# STATE.md — DataMate (Zalo AI Challenge 2026) · cập nhật 12/11/2026

## Checkpoint DF-1 — 14/11/2026
- Đã thêm parser số/ngày strict có trạng thái `ok`/`empty`/`invalid`/`ambiguous`, giữ raw value và `SourceLocation`.
- Đã thêm provenance theo dòng cho CSV/XLSX/SQLite; CSV không còn tạo thêm bản sao `list(csv.reader(...))`; SQLite vẫn mở `mode=ro`.
- XLSX phát hiện header không đủ hoặc có cấu trúc nhiều hàng/gộp ô và trả lỗi rõ ràng thay vì tự gộp cột. Chưa có chính sách header theo từng nguồn.
- Đã chạy 17 test cũ với `PYTHONPATH=src` và smoke test parser; chưa kịp thêm test parser/ingest bền vững vì người dùng yêu cầu dừng và push ngay.
- Việc tiếp theo: thêm test synthetic cho parser và ingestion trước khi chuyển sang iterator/streaming descriptor hoặc Data Discovery.

## Đã xong
- Phiên A (M0–M1): đọc luật và đề, kiểm kê train + public, phân tích rulebook và câu hỏi.
- Báo cáo đầy đủ: Claude Doc “DataMate – Báo cáo Giai đoạn 1 (M0–M1)”.
- Công cụ: `inventory.py` (kiểm kê dữ liệu), `qstats.py` (thống kê câu hỏi và đáp án).
- Phiên B1 (feature/offline-core): ingest CSV/XLSX streaming/SQLite, time parser Gregorian, rule planner, allowlist executor subset (doanh thu/số lượng/số đơn/tỉ lệ huỷ/top bán chạy), verifier, output validator, test synthetic, predict.sh/Dockerfile baseline.
- Phiên B2: API nội bộ không mạng, scorer local kiểu output, trace log từng câu ở /result/logs/trace.jsonl theo Docker Guide.

## Trạng thái hiện tại 13/11/2026
- VERIFIED: unit tests synthetic cho rule subset; output JSONL deterministic; reader XLSX streaming không cần nạp nguyên sheet.
- UNVERIFIED: chạy full train/public, Docker build/run, score, SLM/LLM model/weights, tất cả rules phức tạp.
- Không dùng public/private test để tuning. Không commit dataset/output/weights.

## Chạy lại (cần train.zip, public_test.zip đã giải nén)
```
python inventory.py train/ inv_train.json --titles
python inventory.py public_test/ inv_public.json --titles
python qstats.py train/ 40
python qstats.py public_test/ 15
```

## Phạm vi đã đọc (để phiên sau không nhầm)
- Đọc đầy đủ: rulebook train; chữ trong 4 file Project (file “tổng quan” chỉ có một URL); 3 ảnh.
- calendar.csv: chỉ xem header và 2 dòng đầu; hai bản (train, public) giống hệt nhau.
- Rulebook public: chỉ đọc phần khác biệt so với train (48 dòng). Dòng “Trả góp” của cửa hàng điện thoại bị cắt ở 400 ký tự, cần đọc lại nguyên văn.
- README: chỉ đọc dòng mô tả đầu của 44 file (30 train + 14 public). Cần đọc đầy đủ khi viết loader.
- File dữ liệu: chỉ header, 1–2 dòng mẫu và số dòng; chưa đọc nội dung ô.
- Câu hỏi: thống kê toàn bộ 4.000 câu, chỉ xem tay khoảng 52 câu mẫu.
- Đính chính (13/11): Docker guideline CÓ trong tài liệu Project và đã được đối chiếu (xem `docs/decisions.md`); lịch nộp lấy từ `Submission_Guidance`. Vẫn chưa có: `build-your-own-skill-library.pdf`, nội dung trang challenge.zalo.ai, thông tin GPU của đội.

## Việc kế tiếp — Phiên B (loader + bộ chấm điểm)
1. Đọc đầy đủ README của một business cho mỗi kiểu file (10 kiểu) và ghi chú cấu trúc.
2. Viết loader cho header 2 tầng, sheet theo tháng, ngày và số dạng chữ; đối soát tổng đơn và thanh toán.
3. Viết `scorer.py` đúng luật khớp (chuỗi NFC/lowercase/giữ dấu, số, % hai chữ số, list, table) kèm test từ các ví dụ trong luật.
4. Thước đo xong: tỉ lệ business train đọc đúng theo đối soát.

## Lưu ý môi trường sandbox (tránh lặp lỗi cũ)
- Không GPU, 1 CPU, khoảng 3 GB RAM; có pandas 3.0.6, openpyxl 3.1.5, scikit-learn; không có duckdb.
- Lệnh chạy quá 300 giây bị dừng: chia nhỏ hoặc ghi kết quả trung gian ra file.
- Shell là dash: không dùng `<(...)` hay `time (...)`; in tiếng Việt bằng Python, không dùng `cut -c` hoặc `head -c` vì cắt hỏng UTF-8.
- XLSX thường thiếu thẻ dimension: đếm dòng bằng cách quét thẻ `<row` trong file zip (vài giây).
- web_fetch chỉ mở URL đã xuất hiện trong kết quả tìm kiếm trước đó.
