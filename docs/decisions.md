# Nhật ký quyết định kiến trúc — DataMate

Cập nhật: 13/11/2026. Nhãn: **VERIFIED** (đã kiểm tra trực tiếp trên tài liệu/dữ liệu), **INFERRED** (suy ra từ dữ liệu), **PROPOSED** (đề xuất, chưa kiểm chứng), **UNVERIFIED** (chưa đủ thông tin).

## 1. Quyết định đã được đội xác nhận
| # | Quyết định | Nguồn |
|---|---|---|
| D1 | Hướng kết hợp: SLM hiểu câu hỏi và lập kế hoạch; Python/SQL tính toán xác định; rule engine áp dụng rulebook; kiểm chứng; abstain hoặc unanswerable khi thiếu cơ sở. Mô hình không tự sinh số liệu. | chỉ dẫn ban đầu của đội |
| D2 | Ưu tiên giải pháp nhánh SLM (tổng tham số ≤ 15B). | chỉ dẫn ban đầu của đội |
| D3 | Đọc rulebook/README theo từng split lúc chạy; không hard-code đáp án, id câu hỏi, id business, tên bảng/cột của business đã biết. | chỉ dẫn ban đầu của đội; Rule 4 |
| D4 | Cấu trúc repo: `src/datamate/`, `tests/`, `docs/`, `tools/`, `data/` (chỉ README), `models/` (chỉ README và manifest). | đội xác nhận 13/11 |
| D5 | Chỉ tạo module khi có mã thật. Module dự kiến: `ingest`, `canonical`, `rules`, `timeparse`, `understanding`, `metrics`, `verify`, `output`, `scoring`. Không tạo thư mục rỗng. | đội xác nhận 13/11 |
| D6 | Đã tạo predict.sh và Dockerfile baseline sau khi đối chiếu Docker Guide và người dùng yêu cầu bắt đầu. Base CPU chỉ kiểm giao diện; image final phải CUDA >=12.8/RTX 5090-compatible và được kiểm chứng offline. | code feature/offline-core, 13/11 |
| D7 | Chỉ thêm dependency thực sự cần (hiện: `openpyxl`). | đội xác nhận 13/11 |
| D8 | Không đưa dataset, câu hỏi/đáp án, rulebook cuộc thi, trọng số, credentials vào Git. Dữ liệu giả tự tạo cho kiểm thử được phép ở `tests/fixtures/`. | đội xác nhận 13/11 |
| D9 | Commit nhỏ, thông điệp rõ; liệt kê file thay đổi trước mỗi commit/push; không force push; không push khi chưa có xác nhận. | đội xác nhận 13/11 |

## 2. Chưa quyết định (không coi là sự thật)
- **PROPOSED**: kiến trúc chi tiết (loader, canonicalizer, thẻ luật, planner với Query Spec, executor, verifier, writer); lớp chuẩn hoá thực thể; lộ trình theo phiên; phân công.
- **PROPOSED**: chỉ trả lời khi tin cậy > 50%. Hệ quả toán học của công thức PA (+1/0/−1) là VERIFIED; việc hiệu chuẩn ngưỡng trên dev là PROPOSED.
- **UNVERIFIED**: chọn mô hình SLM cụ thể; fine-tuning; việc dùng rulebook public khi thiết kế engine có phù hợp Rule 6 không (nên hỏi BTC); tên repo và chế độ private.

## 3. Đối chiếu Docker Guide (VERIFIED từ `zac2026_DataMate_docker_guideline_final.pdf` trong tài liệu Project)
- Một image `linux/amd64`, tên `zaic2026_datamate_<team>:final`; tar chưa nén ≤ 100 GB. Base khuyến nghị `vllm/vllm-openai:v0.10.1.1` (đã thử với PyTorch 2.7.1+cu128); phương án khác phải hỗ trợ RTX 5090 (compute capability 12.0).
- Máy chấm: 2 × RTX 5090 (32 GB), RAM 512 GB, CUDA ≥ 12.8, mạng tắt, `/data` chỉ đọc, ghi tạm ở `/tmp`; tối đa 6 giờ cho toàn bộ private test, gồm nạp mô hình.
- Lệnh chấm: `docker run --rm --gpus '"device=0,1"' --network none --shm-size=16g --entrypoint bash -v <test>:/data:ro -v <out>:/result <image> /code/predict.sh`.
- `/code/predict.sh` chạy không đối số, đọc `/data`, ghi `/result/submission.jsonl` và `/result/logs/`; mặc định (model, seed, temperature, batch) cố định trong script; ghi từng đáp án ngay khi có.
- Log mỗi câu: `id`, `answer`, `elapsed_ms`, `thinking` (null nếu không có suy luận sinh ra); câu giải bằng code thì thêm `code` và `output` thực tế.
- Image phải chứa: mã suy luận, mã huấn luyện, dữ liệu huấn luyện/sinh dữ liệu, log, `data_manifest.json`, trọng số (cả base và adapter nếu có), `README.md` (cách tiếp cận, mô hình với nguồn/revision/ngày phát hành/giấy phép/số tham số, dữ liệu). Cấu trúc `/code` gợi ý: `predict.sh`, `README.md`, `requirements.txt`, `src/`, `models/`, `training_code/`. Chỉ `/code/predict.sh` và đường dẫn vào/ra là cố định.
- Tái lập: |PA(đã nộp) − PA(chạy lại)| ≤ 0,03; dùng seed cố định hoặc greedy.
- Lưu ý phân biệt: dữ liệu huấn luyện đi cùng image theo Docker Guide, nhưng KHÔNG đưa vào repository Git (D8).

## 4. Lịch nộp (VERIFIED từ `Submission_Guidance`)
- Public test: 26/10 – 16/11, tối đa 5 lượt nộp kết quả mỗi ngày.
- 16/11, 23:59 (GMT+7): nộp gói Docker đầy đủ (mã huấn luyện, mã suy luận, dữ liệu) qua form; tối đa 2 lần nộp, chỉ lần cuối được chấm; cần checksum và link Google Drive.
- Private test: 9:00 ngày 20/11 phát bộ test; hạn nộp kết quả 23:59 ngày 23/11; hai đội đầu công bố 2/12.
- **UNVERIFIED**: tài liệu giao diện mà đội dán trước đó nói “mỗi đội một lần Test Solution mỗi ngày”, mâu thuẫn với “5 lượt/ngày” ở trên; cần xác nhận lại trên cổng.
