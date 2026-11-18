# Lịch sử rule và extractor

| Phiên bản lock | Thời điểm | Thay đổi | Dữ liệu dẫn tới thay đổi | Ảnh hưởng |
|---|---|---|---|---|
| 1.0.0 | 2026-11-18 10:12 +07:00 | Bản khóa đầu. D0 1.0.0, static-only 1.0.0, extractor 1.0.0 | Phát triển trên B1, B2, P1, TV2C-B3, TV2C-B4 | Chạy được dev và test; probe bị dừng do lỗi extractor |
| 1.0.1 | 2026-11-18 (sau lượt probe đầu) | Extractor 1.0.1: gấp hằng số đúng với số dịch âm; lỗi nội bộ trở thành `analysis_error` thay vì làm dừng cả lượt chạy | Lượt probe của 1.0.0 báo `ValueError: negative shift count`. Không dùng kết quả test để chọn thay đổi | Rule D0 và static-only không đổi. 0/16 kết luận test thay đổi |

## Quy tắc

- Không sửa tệp thuộc lock hiện tại mà không tạo lock mới.
- Giữ nguyên thư mục kết quả của phiên bản cũ.
- Chỉnh rule sau khi xem test phải ghi rõ dữ liệu đã dùng và không được gọi là cùng phiên bản.

## Trạng thái khóa

- `configs/tv2/locks/rule-lock-1.0.0.json`: giữ để truy vết. Không còn khớp code hiện tại, đây là điều mong đợi.
- `configs/tv2/locks/rule-lock-1.0.1.json`: phiên bản hiện tại.
- Commit `1befa67` do người dùng tạo chứa đúng các tệp của lock 1.0.1. Kết quả đối chiếu ở `configs/tv2/locks/lock-commits.json`. Trường `git_commit_lock` trong tệp lock giữ nguyên vì nó ghi trạng thái lúc tạo lock.
- Mốc khóa cuối tuần 7 của nhóm chưa được đối chiếu với lịch thực tế.
