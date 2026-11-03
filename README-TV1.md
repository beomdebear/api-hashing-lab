# Bộ thực hành TV1 cho đồ án API hashing

Đọc `docs/TV1-HUONG-DAN.md` để làm theo thứ tự. Bộ mã này dùng C, Windows x64 và MSVC.
Mọi mẫu chỉ tạo `marker.txt` trong thư mục làm việc. Script kiểm tra tạo thư mục riêng dưới
`artifacts/runs/tv1/` cho mỗi lần chạy; mẫu dùng CREATE_NEW để không ghi đè file có sẵn.

## Đưa vào repo đã có

Giải nén ở một thư mục tạm, mở bằng VS Code, rồi chép các file vào repo theo đường dẫn tương ứng.
Không ghi đè file nhóm đã làm mà chưa xem diff. Bộ này không thay README, .gitignore, manifest hay
runner chung của TV4. Những file tiện ích đều có tiền tố `tv1-`.

Có 9 mẫu: B1, B2, P1, P2, P3, P4, P5, E1, E2. B3–B6 thuộc phần phối hợp TV2/TV4 và không có trong gói này.

## Trạng thái xác minh

- Đã kiểm tra phép hash C với vector chuẩn và đối chiếu mã Python độc lập trong môi trường Linux.
- Đã đối chiếu các hằng số hash được tạo cho P1–P5/E1/E2.
- Chưa build bằng MSVC hoặc chạy trên Windows VM tại nơi tạo gói này.
- Chưa xác minh imports/strings thực tế của binary, collision trên DLL của máy bạn hoặc collector.
- Thực hiện đầy đủ kiểm tra trong hướng dẫn trước khi ghi nhận mẫu đạt yêu cầu.

Đây là bộ mã hỗ trợ triển khai. Minh chứng phải là kết quả bạn thực sự chạy; không dùng tài liệu này
để thay thế ảnh, log hay kết quả đánh giá. Không tắt phần mềm bảo mật để ép mẫu chạy. Nếu bị chặn,
ghi nhận lần chạy bị chặn để điều tra, không xem đó là kết quả detector của nhóm.

## Các file chính

| File | Vai trò |
|---|---|
| `samples/*/*/main.c` | Điểm vào mỗi mẫu và cấu hình lúc build |
| `samples/common/tv1_program.h` | Luồng chương trình và marker dùng chung; chọn nhánh khi biên dịch |
| `samples/common/tv1_hash.h` | DJB2, FNV-1a, CRC32; chỉ biên dịch thuật toán được chọn |
| `samples/common/tv1_resolver.h` | Duyệt tên export của module đã nạp, kiểm tra collision, lấy địa chỉ |
| `scripts/tv1-build.ps1` | Build mẫu hoặc công cụ audit, lưu log và SHA-256 |
| `scripts/tv1-check.ps1` | Kiểm tra mã thoát và marker của từng mẫu; không thu API trace |
| `scripts/tv1-generate-hashes.py` | Tính hằng số hash trước build; không dùng trong detector |
| `tests/resolver/tv1-audit.c` | Kiểm tra tên tìm được và địa chỉ có đúng API mong đợi không |
| `configs/build/tv1-hash-values.csv` | Bảng hash phục vụ kiểm chứng của TV1 |

Việc dùng header chứa code giúp bộ mẫu ban đầu dễ build từ một `main.c`. Khi nhóm tách thành
`.c/.h` riêng, giữ các kiểm tra và tránh liên kết thêm nhánh/thuật toán không dùng vào mỗi mẫu.
