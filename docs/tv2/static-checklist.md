# Static checklist

Danh sách dấu hiệu dự kiến cho phân tích tĩnh. **TV1 chưa xác nhận danh sách này.** Nội dung đã được đối chiếu với source hiện tại và binary build `20261118-094956`.

| # | Dấu hiệu | Vị trí cần xem | Cách kiểm tra | Dễ hiểu nhầm | Đặc trưng tương ứng |
|---:|---|---|---|---|---|
| 1 | API đích có trong bảng import | Import directory, Symbol Tree > Imports | So danh sách import với API cần quan tâm | CRT tự thêm nhiều import. Thiếu import không tự chứng minh hashing | `f.imports.*` |
| 2 | Có `GetProcAddress` | Import và các lời gọi tới ô IAT | Tìm tham chiếu tới ô import | Chương trình hợp lệ cũng dùng | `f.imports.get_proc_address`, `f.code.get_proc_address_calls` |
| 3 | Có nạp hoặc lấy module | `LoadLibrary*`, `GetModuleHandle*` | Xem kết quả có đi vào bước resolve không | CRT cũng dùng `GetModuleHandleW` | `f.imports.loader_apis` |
| 4 | Tên API là hằng chuỗi | Defined Strings, tham chiếu từ mã | Xem chuỗi có đi vào đối số tên của `GetProcAddress` | Chuỗi trong bảng import không phải chuỗi mã đang dùng | `f.resolve.constant_names` |
| 5 | Duyệt bảng export | Đọc `+0x3C`, `+0x88`, `+0x20`, `+0x18` | Theo con trỏ từ module base tới bảng tên | Duyệt export có thể chỉ để so tên bằng `strcmp` | `rel.export_names_enumerated` |
| 6 | Vòng giống hash | Vòng có nạp byte, trộn, kết hợp | Xem hằng, phép nhân, xoay, XOR | Có thể là checksum dữ liệu hoặc mã runtime | `f.code.hash_like_loops` |
| 7 | Tên export đi vào hash | Tham số hoặc byte nguồn của vòng | Theo luồng từ con trỏ tên tới hàm hoặc vòng hash | Hai dấu hiệu cùng có mặt chưa tạo quan hệ | `rel.export_name_to_hash` |
| 8 | Hash được so sánh | `CMP` ngay sau hash | Xác định toán hạng kia là tham số hoặc hằng | Hash có thể chỉ để kiểm tra toàn vẹn | `rel.hash_to_compare` |
| 9 | Phép so quyết định tên được giữ | Khối phụ thuộc vào nhánh so sánh | Xem tên được gán trong nhánh khớp | Không đồng nhất với so chuỗi `strcmp` | `rel.compare_to_name_selection` |
| 10 | Tên đã chọn đi vào resolve | Đối số RDX của `GetProcAddress` | Theo biến tên, kể cả qua tham số out | Resolver khác có thể không dùng `GetProcAddress` | `rel.selection_to_resolve` |
| 11 | Địa chỉ được dùng | `CALL reg` hoặc `CALL [stack]` | Theo giá trị trả về tới đích gọi | Lời gọi trong CRT không liên quan. E1 resolve nhưng không gọi | `rel.resolve_to_pointer_use` |
| 12 | Hằng hash đích | Hằng 32 bit truyền vào resolver | Chỉ dùng để phân tích thủ công | Không đưa bảng hash của PoC vào detector | Không dùng làm đặc trưng |

## Quy tắc ghi bằng chứng

- Ghi binary, SHA-256, image base, hàm, RVA và lệnh.
- Tách điều đã xác minh khỏi suy luận.
- Không ghép địa chỉ hoặc ảnh từ nhiều build.
- Tên `FUN_*` là tên Ghidra đặt, không phải symbol gốc.

## Nội dung cần TV1 xác nhận

1. Bộ dấu hiệu trên có khớp mô tả cơ chế PoC không.
2. Binary và commit nào sẽ được chốt cho đánh giá chính thức.
3. E1 và E2 có giữ nhãn chứa mã API hashing như hướng dẫn TV1 đang ghi không.
