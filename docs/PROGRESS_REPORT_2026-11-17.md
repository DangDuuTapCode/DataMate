# DataMate — Báo cáo tiến trình tổng hợp

**Cập nhật:** 17/11/2026, GMT+7  
**Mục tiêu hiện tại:** tối đa số câu trả lời đúng trên Public Test 1.000 câu, đồng thời abstain khi thiếu bằng chứng. Đây là mục tiêu, chưa phải kết quả đo được.

## Tóm tắt

- DataMate là hệ thống hỏi đáp tiếng Việt trên dữ liệu bán hàng, dùng phép tính xác định và cơ chế abstain. Nền tảng ingestion, chuẩn hóa, lập kế hoạch câu hỏi, kiểm tra bằng chứng và xuất output đã được phát triển qua nhiều vòng.
- P1 (khảo sát cấu trúc 30 business) và P2 (đối soát ingestion) có bằng chứng hoàn tất ở phạm vi cấu trúc. Reviewer độc lập P3 được bỏ qua theo chỉ đạo, vì vậy P3 vẫn **NOT VERIFIED / NOT PASSED**. P4–P7 có nhiều phần đã sửa và kiểm chứng nhưng chưa đạt toàn bộ tiêu chí nghiệm thu Playbook; P8–P9 chưa có bằng chứng nghiệm thu.
- v26 được chấm sau khi đóng băng dự đoán trên **3.000 câu train**: **237 đúng, 6 sai, 2.757 abstain**; độ chính xác trong các câu đã trả lời **97,53%**, coverage **8,10%**, PA **7,70%**, không có lỗi runtime. Đây là chẩn đoán in-sample, không dự báo điểm public/private.
- So với v25, v26 giữ 237 đúng, giảm câu sai từ 8 xuống 6 và tăng abstain từ 2.755 lên 2.757. Hai false answer bị chặn; số câu đúng chưa tăng trong lượt này.
- Mục tiêu 990/1.000 hoặc tối đa câu đúng chưa đạt và không thể kết luận từ train. Không đọc nhãn public/private, không tuning bằng câu hỏi public.
- `public_submission.jsonl` hiện có là file cũ: 1.000 dòng, 998 abstain và 2 number; SHA-256 `4c79b98f20cb1de5d447856d770b23abd381964b3a1c43ba6b7c1ebb2abad288`. Không xem đây là output v26 hay artifact sẵn sàng nộp. Một candidate public cũ khác từng được xác nhận cấu trúc 282 answered / 718 abstain; nó cũng không có accuracy và không đại diện code v26.

## Tiến trình theo thời gian

### 12–14/11 — nền tảng và DF-1

- Dựng khung repository, pipeline offline, output có kiểu, ingestion và chấm điểm cơ bản.
- DF-1 bổ sung chuẩn hóa số/ngày với trạng thái `ok`, `empty`, `invalid`, `ambiguous`; hỗ trợ ngày Excel 1900/1904, provenance theo dòng, CSV incremental hơn, ingestion XLSX/SQLite.
- Đây là nền tảng từng phần, không phải hoàn tất toàn bộ Data Foundation.

### 15/11 — P0, P1, P2 và phát triển P3

- P0 xác định repository thật `DataMate`, nhánh làm việc `feature/offline-core`, tạo snapshot riêng từ base `24cfa0908bd20f6e5b210366e956cae0d665b56e`; `main`, archive/reference và nguồn đồng bộ được giữ riêng.
- P1 structural profile: 30/30 business, 128 file dữ liệu, 339 bảng/sheet, 3.997.042 dòng census và README của 30 business. Đây là bằng chứng đọc cấu trúc, không xác nhận mọi đáp án đúng.
- P2 reconciliation: 30/30 business, 128 file, 339/339 bảng/sheet; 3.997.277 dòng nguồn = 3.997.042 accepted + 0 rejected + 235 skipped; không lỗi file.
- P3 phát triển QuerySpec, intent, thời gian, đơn vị, alias, entity và evaluator. Reviewer độc lập bị bỏ qua; không có annotation độc lập hoặc bằng chứng đạt 81%, nên P3 vẫn NOT PASSED.
- Tạo và kiểm tra cấu trúc candidate JSONL public cũ; không có nhãn public để đo accuracy.

### 16/11 — reliability, quy tắc nghiệp vụ và replay P6

- Củng cố executor fail-closed, reason code, typed verifier, nhận biết trạng thái đơn; tách revenue khỏi tiền thu; chuẩn hóa VND; hỗ trợ lịch âm/dương và `rulebook.md`/`calendar.csv`.
- Bổ sung join chi tiết–hóa đơn bằng khóa duy nhất, Excel date epoch, suy luận dấu phân cách số khi toàn cột có bằng chứng nhất quán, loại ledger nhập hàng khỏi thống kê bán, ưu tiên số lượng cơ sở và loại dòng tổng bị cộng lặp.
- P7 structural matrix có hồ sơ cho 30/30 business; các mức hỗ trợ nghiệp vụ cao hơn chưa được nghiệm thu. Không công bố phần trăm hoàn thành tổng dự án.
- Một số replay cũ bị loại khỏi đánh giá do thiếu metadata hoặc lỗi freeze; không dùng chúng làm kết quả chất lượng.

### 17/11 — v26 và trạng thái mới nhất

- Parser abstain cho filter ca sáng/chiều chưa có executor; câu ranking nhà cung cấp không bị nhận nhầm thành ranking sản phẩm; nhận diện typo `nawm` trong khoảng YTD.
- Executor quy đổi bao bì sang đơn vị cơ sở chỉ khi catalog/conversion metadata chỉ rõ; thiếu mapping thì abstain.
- Test pipeline: **69/69 passed**. Full suite: **189 tests, 186 passed, 3 Git-dependent skips**, exit 0.
- v26 train replay sinh không đọc answer labels, đóng băng và xác minh 3.000 prediction/trace, ID/order/schema và checksum trước khi evaluator mở nhãn train.
- Còn 6 false answers train: 3 trường hợp tỷ lệ hủy có vẻ khác nhãn train so với `rulebook.md` (quy ước hiện tại: chỉ đơn hủy trên toàn bộ đơn); 3 câu sales ranking. Không đổi quy tắc chỉ để khớp nhãn mâu thuẫn.

## Các replay train tiêu biểu

| Phiên bản | Đúng | Sai | Abstain | Ghi chú |
|---|---:|---:|---:|---|
| v5 | 45 | 60 | 2.895 | 3.000 câu; PA -0,50%; lỗi revenue chiếm phần lớn |
| v7 | 47 | 37 | 2.916 | PA 0,33%; in-sample |
| v16 | 26 | 4 | 2.970 | PA 0,733%; coverage 1,00% |
| v17 | 26 | 3 | 2.971 | PA 0,767% |
| v18 | 28 | 10 | 2.962 | PA 0,600%; regression |
| v19 | 30 | 4 | 2.966 | PA 0,867% |
| v22 | 181 | 54 | 2.765 | PA 4,233%; vẫn nhiều lỗi |
| v23 | 223 | 9 | 2.768 | PA 7,133% |
| v24 | 225 | 6 | 2.769 | PA 7,300%; answered accuracy 97,40% |
| v25 | 237 | 8 | 2.755 | PA 7,633%; mở rộng sales-detail joins |
| **v26** | **237** | **6** | **2.757** | **PA 7,700%; answered accuracy 97,53%; coverage 8,10%** |

> Tất cả là train diagnostics in-sample. Không suy diễn các phiên bản không liệt kê là cải thiện. Không so trực tiếp với Public Test 1.000 câu.

## Bằng chứng tái kiểm tra

- Snapshot: `work/rehydrated-2026-11-15-P3/source`, không có `.git`, theo base `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Input train: `work/evaluation/train-inputs-2026-11-16-with-split-metadata`.
- Replay v26: `work/evaluation/p6-train-replay-v26-fail-closed-unit-conversion-2026-11-16/`.
- Score report SHA-256: `c466fdd745c79125c32c91f9057221a397b17ff578ab79a2a0596b750399ec38`.
- Freeze: 3.000 câu, 30 business, `answer_labels_accessed=false` khi sinh. Input manifest `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; code manifest `557fa204c5a8efc5fa5ad7a1529bf4eee774cb4476ad9745b500a767c9ec8bd9`; prediction `2eed2edf53b6ebef31aa67206e1a56040d4f7fb311794c5cb14bcaf23571b59d`; trace `56fc14bed21d18855f7233e1c0a8699af10e9e4c06db7a8ee60acf98326c9c6d`.
- Lệnh kiểm tra:
  - `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 69/69 passed.
  - `PYTHONPATH=src python -m unittest discover -s tests -v` — 189 run, 186 passed, 3 Git-only skips.
  - `PYTHONPATH=src python tools/replay_predictions.py --data-root work/evaluation/train-inputs-2026-11-16-with-split-metadata --output-dir work/evaluation/p6-train-replay-v26-fail-closed-unit-conversion-2026-11-16 --source-root .`
  - `PYTHONPATH=src python tools/evaluate_replay.py --replay-dir work/evaluation/p6-train-replay-v26-fail-closed-unit-conversion-2026-11-16 --data-root work/evaluation/train-inputs-2026-11-16-with-split-metadata --train-archive sources/train.zip --report work/evaluation/p6-train-replay-v26-fail-closed-unit-conversion-2026-11-16/score-report.json`

## GitHub và phạm vi đồng bộ

- Nội dung trên GitHub `main` của các module triển khai và regression test chính v26 đã được so với snapshot, khớp sau khi chuẩn hóa line ending. Lượt đồng bộ này chỉ thêm/cập nhật tài liệu, không thay đổi code.
- Đồng bộ báo cáo tổng hợp và cập nhật tham chiếu tại `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, `tools/STATE.md` cùng checkpoint lên `main`; dùng commit bình thường qua GitHub API, không force-push hoặc sửa lịch sử.
- Snapshot local không có `.git`, không dùng để tuyên bố trạng thái Git. Checkout local riêng được đọc ở `feature/offline-core`, commit `3b0bf3b66e9a78fa68fa29e8b97a23787bac2f0a`, sạch tại thời điểm kiểm tra. Không đổi nhánh local.

## Việc còn lại

1. Điều tra ba lỗi ranking bằng schema/evidence, sửa quy đổi đơn vị một cách tổng quát và thêm regression.
2. Giữ nguyên quy tắc hủy trong rulebook; phân tích khác biệt nhãn, không đổi công thức để chạy theo đáp án train.
3. Chỉ tăng coverage khi intent/filter có executor và evidence đầy đủ; filter chưa hỗ trợ phải abstain.
4. Chạy replay train mới sau khi đóng băng code; kiểm tra checksum trước khi evaluator đọc nhãn.
5. Khi code ổn định, tạo Public Test JSONL một lượt để kiểm cấu trúc/runtime; không dùng câu hỏi public để tuning, không đọc nhãn private, không tuyên bố accuracy public khi chưa có kết quả chính thức.
6. Chưa có bằng chứng artifact public v26 được tạo, Docker/Test Solution được dựng hoặc portal được submit.


