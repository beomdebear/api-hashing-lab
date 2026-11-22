# Bộ thực hành TV1 cho đồ án API hashing

Đọc `docs/TV1-HUONG-DAN.md` để làm theo thứ tự. Bộ mã này dùng C, Windows x64 và MSVC.
Mọi mẫu chỉ tạo `marker.txt` trong thư mục làm việc. Script kiểm tra tạo thư mục riêng dưới
`artifacts/runs/tv1/` cho mỗi lần chạy; mẫu dùng CREATE_NEW để không ghi đè file có sẵn.

## Đưa vào repo đã có

Giải nén ở một thư mục tạm, mở bằng VS Code, rồi chép các file vào repo theo đường dẫn tương ứng.
Không ghi đè file nhóm đã làm mà chưa xem diff. Bộ này không thay README, .gitignore, manifest hay
runner chung của TV4. Những file tiện ích đều có tiền tố `tv1-`.

Có 9 mẫu: B1, B2, P1, P2, P3, P4, P5, E1, E2. B3–B6 thuộc phần phối hợp TV2/TV4 và không có trong gói này.

## Trạng thái xác minh (cập nhật sau kiểm thử trên Windows VM)

- Linux (2026-10-31): đã test vector/hash C/Python; `docs/TV1-VALIDATION.txt` phản ánh đúng phạm vi Linux lịch sử, không phải xác minh Windows.
- Windows 10 x64 VM, MSVC x64: B1, B2, P1 đã build và chạy checker v2 thành công (mỗi mẫu 1 run), exit code 0, marker tồn tại và đúng nội dung. Chi tiết build ID, run ID và SHA trong `evidence/G1/TV1/G1-TV1-02/README.md` và `G1-TV1-03/README.md`.
- Audit DJB2 trên Windows: 3 API đúng tên/địa chỉ, matches=1; exit 0. Manifest của **audit** xác nhận MSVC 19.51.36260.0, x64.
- B1/B2 imports đã quan sát qua dumpbin theo bằng chứng terminal trước đó. Chưa xác minh strings đầy đủ, Windows full build/snapshot và compiler version riêng của từng build B1/B2/P1 trong lần cập nhật này.
- `collector_status=not_collected`: **chưa có dynamic API trace độc lập**, TV3 sẽ thực hiện.
- Binaries/manifest/log/marker gốc ở `artifacts/` (Git ignore); TV1 cần xác nhận còn file trên VM và đối chiếu nguồn commit tại thời điểm build.
- TV3 nhận binary hoặc tự build theo `docs/TV1-TV3-HANDOFF.md`.
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
