# Bảng trạng thái bằng chứng — kết quả M0–M1

Nguồn: báo cáo “DataMate – Báo cáo Giai đoạn 1 (M0–M1)” và các lần kiểm tra sau đó. Chỉ ghi nhận định đã có cơ sở theo nhãn tương ứng.

## VERIFIED
- Công thức PA = trung bình s_i với đúng +1, abstain 0, sai −1; type phải trùng type chuẩn; câu unanswerable chỉ đúng khi đáp án chuẩn là unanswerable.
- Train: 30 business, 3.000 câu có đáp án; public: 14 business, 1.000 câu không đáp án. Định dạng file: train 107 xlsx, 20 csv, 1 sqlite; public 69 xlsx, 10 csv, 1 sqlite.
- Kiểu đáp án train: number 62,8%; percent 19,3%; list 6,4%; date 4,8%; string 2,9%; unanswerable 2,3% (70/3.000); boolean 0,8%; table 0,6%. Mọi number là số nguyên.
- Rulebook train 14.650 ký tự, rulebook public 18.799 ký tự, khác nhau 48 dòng; public thêm 3 ngành (mẹ và bé, sửa xe, cửa hàng điện thoại), 11 dòng luật chung mới và bỏ 3 dòng luật so với train. `calendar.csv` hai split giống hệt nhau.
- Tổng số dòng mỗi business: train trung vị 113.571 (26.119–305.989); public trung vị 88.039 (6.104–302.800).
- Đặc điểm dữ liệu quan sát trực tiếp: header 2 tầng/gộp ô, sheet theo tháng, ngày và số dạng chữ, tên cột và giá trị khác nhau theo business.
- Nội dung Docker Guide và lịch nộp: xem `docs/decisions.md` phần 3 và 4.
- Sandbox của phiên phân tích: không GPU, 1 CPU, khoảng 3 GB RAM, không có mạng.

## INFERRED
- 10 kiểu xuất file ở train (suy từ câu mô tả đầu của README, chưa đọc đầy đủ README).
- Câu hỏi khuôn mẫu: gom cụm TF-IDF thô cho 143 cụm; 50 cụm đầu phủ khoảng 80% train.
- Tỉ lệ các họ ý định và mức nhiễu ngôn ngữ (regex thô); xu hướng public dùng ký hiệu thời gian viết tắt nhiều hơn.
- Thứ tự các nguồn gây mất điểm (mục 7 báo cáo).

## PROPOSED
- Kiến trúc pipeline, lớp chuẩn hoá thực thể, ngưỡng abstain > 50% có hiệu chuẩn, lộ trình theo phiên, phân công, rejection-sampling fine-tuning.

## UNVERIFIED
- Nội dung `build-your-own-skill-library.pdf` (chưa có trong tài liệu).
- Nội dung trang challenge.zalo.ai (chưa mở được).
- Số lượt nộp mỗi ngày (5 lượt hay 1 lượt).
- Ứng viên SLM; GPU của đội; ranh giới dùng rulebook public theo Rule 6.
- Toàn văn dòng “Trả góp” (cửa hàng điện thoại) trong rulebook public; toàn văn README.

## Đính chính báo cáo M0–M1
1. Báo cáo ghi file Docker guideline “không có trong file tải lên”. Điều này SAI: file có trong tài liệu Project. Các mục Docker trước đây gắn UNVERIFIED nay là VERIFIED (xem `docs/decisions.md`). Chỉ `build-your-own-skill-library.pdf` là còn thiếu.
2. Lộ trình phiên A–G trong báo cáo chưa tính hạn nộp Docker 16/11; cần rút gọn theo lịch thật.
3. Mục 5 của báo cáo liệt kê 12 mục dưới “11 luật chung”; thực tế “trả hàng sau kỳ” là chỉnh sửa luật sẵn có, không phải dòng luật mới.
