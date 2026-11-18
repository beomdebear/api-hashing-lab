# Ví dụ thiếu bằng chứng

Thứ tự quan hệ: duyệt tên export > tên → hash > hash → so sánh > so sánh → chọn tên > tên → resolve > resolve → dùng con trỏ.

| Trường hợp | Ý nghĩa | analysis.status | Trạng thái quan hệ | Static-only |
|---|---|---|---|---|
| synthetic-truncated-P1 | Fixture tổng hợp: cắt P1 còn 0x180 byte | error | lỗi phân tích > lỗi phân tích > lỗi phân tích > lỗi phân tích > lỗi phân tích > lỗi phân tích | unknown |
| synthetic-wrong-machine-P1 | Fixture tổng hợp: đổi trường Machine của P1 thành x86 | unsupported | chưa xác định > chưa xác định > chưa xác định > chưa xác định > chưa xác định > chưa xác định | unknown |
| synthetic-compare-removed-P1 | Fixture tổng hợp: thay lệnh so sánh hash của P1 bằng NOP | ok | đã xác minh > đã xác minh > không thấy > không thấy > không thấy > không thấy | negative |
| TV2C-B6 | Mẫu thật: có duyệt export nhưng thiếu bước hash | ok | đã xác minh > không thấy > không thấy > không thấy > không thấy > không thấy | negative |
| E1 | Mẫu thật: có resolve nhưng không dùng địa chỉ | ok | đã xác minh > đã xác minh > đã xác minh > đã xác minh > đã xác minh > gợi ý | positive |
| B2 | Mẫu thật: không có chuỗi export | ok | không thấy > không thấy > không thấy > không thấy > không thấy > không thấy | negative |

Fixture tổng hợp chỉ dùng để kiểm tra cách biểu diễn thiếu bằng chứng. Chúng không thuộc tập đánh giá.
