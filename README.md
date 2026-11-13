# DataMate — Zalo AI Challenge 2026

Hệ thống trả lời câu hỏi tiếng Việt trên dữ liệu doanh nghiệp nhỏ (CSV, XLSX, SQLite). Mục tiêu của đội: hệ thống SLM (tổng tham số ≤ 15B) tổng quát hoá sang doanh nghiệp và ngành chưa từng gặp.

**Trạng thái:** baseline offline đang hoạt động cho ingest CSV/XLSX/SQLite, planning xác định, executor allowlist, kiểm chứng và JSONL output. Đây chưa phải solution cạnh tranh hoàn chỉnh: join phức tạp, kho/công nợ/lô, lịch âm, và SLM thực tế còn chưa hoàn thiện.

## Hướng tiếp cận đã thống nhất
Kết hợp: SLM hiểu câu hỏi và lập kế hoạch; Python/SQL tính toán xác định; rule engine áp dụng rulebook; bước kiểm chứng; biết abstain hoặc báo unanswerable khi thiếu dữ liệu. Mô hình ngôn ngữ không được tự tạo số liệu. Chi tiết và trạng thái từng quyết định: [`docs/decisions.md`](docs/decisions.md).

## Cấu trúc repository
| Thư mục | Nội dung |
|---|---|
| `src/datamate/` | ingest, time parse, planner, executor, verifier, output |
| `tests/` | kiểm thử; `tests/fixtures/` chỉ chứa dữ liệu GIẢ tự tạo |
| `docs/` | quyết định kiến trúc, bảng trạng thái bằng chứng |
| `tools/` | script phân tích dữ liệu (`inventory.py`, `qstats.py`) và `STATE.md` |
| `data/` | chỉ có `README.md`; dữ liệu cuộc thi đặt cục bộ, bị `.gitignore` chặn |
| `models/` | chỉ có `README.md` (và `manifest.json` khi cần); KHÔNG chứa weights |

Các module dự kiến trong `src/datamate/` (chỉ tạo khi có mã thật): `ingest`, `canonical`, `rules`, `timeparse`, `understanding`, `metrics`, `verify`, `output`, `scoring`. Thư mục `configs/` và `training_code/` tạo khi cần.

## Quy tắc phát triển
1. Không đưa lên Git: dataset gốc, câu hỏi/đáp án (train, public, private), rulebook của cuộc thi, kết quả chạy, log, trọng số mô hình, khoá/thông tin đăng nhập. Chỉ dữ liệu giả tự tạo mới được vào `tests/fixtures/`.
2. Không huấn luyện hay tinh chỉnh trên dữ liệu public/private test; không hard-code đáp án, id câu hỏi hoặc id business.
3. Mọi con số do code xác định tính; không để mô hình sinh số liệu.
4. Ghi nhãn bằng chứng trong tài liệu: VERIFIED, INFERRED, PROPOSED, UNVERIFIED.
5. Commit nhỏ, thông điệp rõ (`chore:`, `docs:`, `feat:`, `test:`); trước mỗi commit hoặc push, liệt kê file thay đổi và mục đích.
6. Không force push; `main` luôn ở trạng thái chạy được; làm việc trên nhánh `feature/<tên>`.

## Chạy cục bộ và kiểm tra
```
python -m unittest discover -s tests -v
```

Runtime không gọi API hay mạng. Rule planner là fallback an toàn; JsonPlanAdapter là extension point để nhận JSON từ SLM/LLM chạy local trong image, kiểm tra strict schema và chỉ cho executor allowlist chạy. Mô hình, weights, license, revision và tổng parameter phải khai báo ở models/manifest.json trước khi tích hợp.

Docker guideline yêu cầu gọi /code/predict.sh, đọc /data và ghi /result/submission.jsonl. Dockerfile hiện là baseline CPU để test giao diện; phải thay base image bằng image CUDA >=12.8 tương thích RTX 5090 và kiểm chứng offline trước khi final.
Bài kiểm tra vệ sinh repo (`tests/test_repo_hygiene.py`) từ chối file dữ liệu, trọng số, file quá lớn hoặc chuỗi giống khoá bí mật trong các file đang được Git theo dõi.

## Công cụ phân tích (cần dữ liệu cục bộ)
```
pip install -r requirements.txt
python tools/inventory.py <thư_mục_split> <inventory.json> --titles
python tools/qstats.py <thư_mục_split> 40
```
