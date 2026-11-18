# Chuỗi bằng chứng API hashing trong P1

- Binary: `P1.exe`, SHA-256 `0277D53B1124978B29154BFA4C11CA62E69CCCF4AF614199DA8D2A5401366787`, build `20261118-094956`.
- Image base tĩnh: `0x140000000`. Mọi địa chỉ thuộc cùng binary này. VA ở đây là VA tĩnh, không phải VA lúc chạy.
- Tên `FUN_*` là tên Ghidra tự đặt. Binary không có PDB nên không có symbol gốc của các hàm này.
- Mỗi lệnh dưới đây được extractor nêu và đã khớp RVA, mnemonic trong disassembly của Ghidra (xem `ghidra-crosscheck.csv`).

| Bước | Module + RVA | VA tĩnh | File offset | Hàm | Lệnh | Quan hệ quan sát | Mức |
|---|---|---|---|---|---|---|---|
| 1. Duyệt bảng export | P1.exe + 0x1196 | 0x140001196 | 0x596 | FUN_1400010b0 (RVA 0x10B0) | `mov rax, qword ptr [rcx + rax + 0x88]` | đọc RVA của export directory tại NT headers +0x88 (PE32+) | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x11EF | 0x1400011EF | 0x5EF | FUN_1400010b0 (RVA 0x10B0) | `cmp dword ptr [rax + 0x20], 0` | đọc AddressOfNames tại export directory +0x20 | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x120E | 0x14000120E | 0x60E | FUN_1400010b0 (RVA 0x10B0) | `mov ecx, dword ptr [rax + 0x20]` | đọc AddressOfNames tại export directory +0x20 | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x1229 | 0x140001229 | 0x629 | FUN_1400010b0 (RVA 0x10B0) | `mov eax, dword ptr [rax + 0x20]` | đọc AddressOfNames tại export directory +0x20 | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x1275 | 0x140001275 | 0x675 | FUN_1400010b0 (RVA 0x10B0) | `mov ecx, dword ptr [rcx + rax*4]` | đọc RVA tên theo chỉ số từ AddressOfNames | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x1294 | 0x140001294 | 0x694 | FUN_1400010b0 (RVA 0x10B0) | `mov eax, dword ptr [rcx + rax*4]` | đọc RVA tên theo chỉ số từ AddressOfNames | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x12B0 | 0x1400012B0 | 0x6B0 | FUN_1400010b0 (RVA 0x10B0) | `mov eax, dword ptr [rcx + rax*4]` | đọc RVA tên theo chỉ số từ AddressOfNames | Đã xác minh |
| 1. Duyệt bảng export | P1.exe + 0x129C | 0x14000129C | 0x69C | FUN_1400010b0 (RVA 0x10B0) | `add rcx, rax` | module base + RVA tên tạo con trỏ tên export | Đã xác minh |
| 2. Hash tên export | P1.exe + 0x12DD | 0x1400012DD | 0x6DD | FUN_1400010b0 (RVA 0x10B0) | `call 0x140001000` | con trỏ tên export được truyền vào hàm giống hash tại RVA 0x1000 | Đã xác minh |
| 3. So sánh hash | P1.exe + 0x12E2 | 0x1400012E2 | 0x6E2 | FUN_1400010b0 (RVA 0x10B0) | `cmp eax, dword ptr [rsp + 0x78]` | hash của tên export được so với tham số hàm | Đã xác minh |
| 4. Chọn tên khi khớp | P1.exe + 0x1306 | 0x140001306 | 0x706 | FUN_1400010b0 (RVA 0x10B0) | `mov rcx, qword ptr [rsp + 0x58]` | con trỏ tên chỉ được gán khi phép so hash chọn nó | Đã xác minh |
| 4. Chọn tên khi khớp | P1.exe + 0x130B | 0x14000130B | 0x70B | FUN_1400010b0 (RVA 0x10B0) | `mov qword ptr [rax], rcx` | con trỏ tên chỉ được gán khi phép so hash chọn nó | Đã xác minh |
| 5. Resolve bằng tên đã chọn | P1.exe + 0x13B1 | 0x1400013B1 | 0x7B1 | FUN_140001360 (RVA 0x1360) | `call qword ptr [rip + 0x1c59]` | tên được chọn bằng hash được truyền vào GetProcAddress | Đã xác minh |
| 6. Dùng con trỏ | P1.exe + 0x15B1 | 0x1400015B1 | 0x9B1 | FUN_1400013f0 (RVA 0x13F0) | `call qword ptr [rsp + 0x68]` | đích lời gọi là địa chỉ GetProcAddress trả về từ tên đã chọn | Đã xác minh |

## Quan hệ giữa các bước

1. `FUN_1400010b0` đọc export directory của module truyền vào, rồi tạo con trỏ tên bằng `base + AddressOfNames[i]`.
2. Con trỏ tên được truyền vào `FUN_140001000`. Hàm này lặp trên từng byte với `h = h * 33 + byte`, seed `0x1505`.
3. Giá trị trả về được so với tham số thứ hai của `FUN_1400010b0`.
4. Khối chạy khi khớp ghi con trỏ tên ra tham số out. Quan hệ này là phụ thuộc điều khiển vào phép so sánh.
5. `FUN_140001360` lấy tên đó và truyền vào `GetProcAddress`. API nhận **tên**, không nhận hash.
6. Địa chỉ trả về đi qua tham số out về `FUN_1400013f0` và trở thành đích của `CALL [RSP+0x68]`.

## Suy luận của người phân tích, tách khỏi bằng chứng trên

Ba hằng dưới đây nằm trong `FUN_1400013f0`. Việc chúng ứng với API nào là phép tính DJB2 độc lập trên tên API công khai, không phải điều binary tự khai. Detector không dùng bảng này.

| API | DJB2 tính độc lập | Lệnh chứa hằng trong binary |
|---|---|---|
| CreateFileW | 0xEB96C610 | `RVA_00001446  MOV dword ptr [RSP + 0x90],0xeb96c610` |
| WriteFile | 0x663CECB0 | `RVA_00001451  MOV dword ptr [RSP + 0x94],0x663cecb0` |
| CloseHandle | 0x3870CA07 | `RVA_0000145C  MOV dword ptr [RSP + 0x98],0x3870ca07` |

Phân tích tĩnh không xác định địa chỉ thực lúc chạy. Với forwarded export, địa chỉ trả về có thể nằm ở module khác như KernelBase.

## Trạng thái ảnh

Ảnh decompile có chú thích từ GUI chưa có. Bản văn bản ở `p1-decompile-annotated.md` lấy từ decompiler chạy headless.
