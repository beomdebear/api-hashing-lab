# Đặc trưng tĩnh TV2

Schema: `schemas/tv2/static-features-1.0.schema.json`. Mã trích xuất: `detectors/tv2/tv2features.py`, `detectors/tv2/tv2analysis.py`.

Schema này là hợp đồng do TV2 đề xuất. Nhóm chưa thống nhất giao diện chung.

## Trạng thái

| Loại | Giá trị | Ý nghĩa |
|---|---|---|
| Quan sát | `present` | Thấy dấu hiệu |
| Quan sát | `absent` | Phân tích xong và không thấy |
| Quan hệ | `verified` | Có đường dữ liệu hoặc phụ thuộc điều khiển trong binary |
| Quan hệ | `heuristic` | Các đầu mối cùng tồn tại, chưa chứng minh được liên kết |
| Quan hệ | `absent` | Phân tích xong và không thấy |
| Cả hai | `unknown` | Phân tích chưa đủ hoặc binary ngoài phạm vi |
| Cả hai | `analysis_error` | Không phân tích được tệp |

## Đặc trưng quan sát

| ID | Kiểu | Ý nghĩa | Cách trích | Bằng chứng |
|---|---|---|---|---|
| `f.imports.get_proc_address` | boolean | Có import `GetProcAddress` | Bảng import | Ô IAT |
| `f.imports.loader_apis` | mảng tên | Có `LoadLibrary*`, `GetModuleHandle*` | Bảng import | Tên trong giá trị |
| `f.code.hash_like_loops` | số nguyên | Số vòng có nạp byte, trộn và kết hợp | Quét lệnh trong các hàm | Lệnh nạp, trộn, kết hợp, cạnh lùi |
| `f.code.non_import_indirect_calls` | số nguyên | Số lời gọi gián tiếp không qua ô IAT | Quét lệnh | Vị trí `CALL` |
| `f.code.get_proc_address_calls` | số nguyên | Số nơi gọi `GetProcAddress` | Tham chiếu IAT và thunk | Vị trí `CALL` |
| `f.resolve.constant_names` | mảng chuỗi | Tên hằng đi vào `GetProcAddress` | Luồng dữ liệu | Vị trí `CALL` và tên |
| `f.resolve.dynamic_name_calls` | số nguyên | Lời gọi có tên không phải hằng trực tiếp | Luồng dữ liệu | Vị trí `CALL` |

## Đặc trưng quan hệ

| ID | Câu hỏi | Điều kiện `verified` |
|---|---|---|
| `rel.export_names_enumerated` | Chương trình có tạo con trỏ tên từ bảng export không? | Có đọc export directory, `AddressOfNames`, phần tử tên và cộng với base |
| `rel.export_name_to_hash` | Byte tên export có đi vào phép trộn trong vòng lặp không? | Con trỏ tên vào hàm giống hash hoặc vòng inline |
| `rel.hash_to_compare` | Kết quả hash có được so sánh không? | `CMP`, `SUB` hoặc `XOR` đặt cờ cho nhánh ngay sau đó |
| `rel.compare_to_name_selection` | Phép so có quyết định tên được giữ không? | Tên được gán trong khối phụ thuộc điều khiển vào phép so |
| `rel.selection_to_resolve` | Tên đã chọn có vào `GetProcAddress` không? | Tên tới đối số RDX, kể cả qua lời gọi và tham số out |
| `rel.resolve_to_pointer_use` | Địa chỉ trả về có được gọi không? | Giá trị trả về trở thành đích `CALL` gián tiếp |

## Tính ổn định và chống rò rỉ

- `content_sha256` không gồm thời gian, ID phiên hay đường dẫn. Đổi tên hoặc chuyển thư mục cùng binary không đổi giá trị này.
- Extractor chỉ nhận byte của một tệp. Test `tests/tv2/test_tv2.py` kiểm tra đổi tên và quét mã để tránh đọc nhãn hoặc bảng hash.
- Runner sao chép binary sang tên trung tính trước khi phân tích.

## Dữ liệu

- Tập phát triển: `evidence/G2/TV2/G2-TV2-03/features-dev-summary.md`.
- Ví dụ thiếu bằng chứng: `evidence/G2/TV2/G2-TV2-03/missing-evidence-examples.md`.
- Đối chiếu với Ghidra: `evidence/G2/TV2/G2-TV2-03/ghidra-crosscheck.csv`.

## Giới hạn

- Phạm vi hiện tại là PE32+ x86-64.
- Phân tích dựa trên `.pdata` và lời gọi trực tiếp để tìm hàm.
- Resolver không dùng `GetProcAddress`, hoặc tự tính địa chỉ qua bảng ordinal, chưa được mô hình hóa.
- Mã GCC `-O2` có resolver inline chưa được truy hết chuỗi.
