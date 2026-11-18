# So sánh B1 và B2 trên binary

Nguồn số liệu: export headless của Ghidra 12.2 trong `ghidra-headless/` và đặc trưng của extractor. Đây chưa phải ảnh GUI.

| Mẫu | SHA-256 | Import liên quan | Chuỗi tên API | Lời gọi API trong mã người dùng | Gọi gián tiếp qua con trỏ | Vòng giống hash | Tên export → hash |
|---|---|---|---|---|---|---|---|
| B1 | 1B52E1BC5C2CA66B7388DFD6AE2E15A5D296541487D9DAB2BC9345B2D87636D8 | CloseHandle, CreateFileW, WriteFile | CreateFileW @0x29FA (tham chiếu: không có tham chiếu); WriteFile @0x2A08 (tham chiếu: không có tham chiếu); CloseHandle @0x2A14 (tham chiếu: không có tham chiếu) | 0x1048 CreateFileW; 0x1099 WriteFile; 0x10A8 CloseHandle | không có | 0 | không thấy |
| B2 | 4332381DAC1948769C6A4D7BD02800A09302678907044FDF7A211DA1DA9446CE | GetProcAddress, LoadLibraryW | CreateFileW @0x3038 (tham chiếu: 0x1058); WriteFile @0x3048 (tham chiếu: 0x106F); CloseHandle @0x3058 (tham chiếu: 0x1086) | 0x1027 LoadLibraryW; 0x1064 GetProcAddress; 0x107B GetProcAddress; 0x1092 GetProcAddress | 0x1102 `CALL qword ptr [RSP + 0x68]`; 0x1151 `CALL qword ptr [RSP + 0x70]`; 0x115E `CALL qword ptr [RSP + 0x78]` | 0 | không thấy |

## Kết luận từ bằng chứng

- B1 import sẵn ba API file và gọi chúng qua ô IAT. Dạng lệnh `CALL [IAT]` là gián tiếp về cú pháp nhưng đích do loader điền từ bảng import.
- Tên API cũng xuất hiện trong B1, nhưng Ghidra không thấy mã nào tham chiếu các chuỗi đó. Chúng thuộc dữ liệu tên của bảng import.
- B2 không import ba API này. Nó có `LoadLibraryW`, `GetProcAddress`, và mã chương trình tham chiếu trực tiếp các hằng chuỗi tên API trước khi gọi `GetProcAddress`, rồi gọi qua con trỏ. Đây là resolve động theo tên.
- B2 không có vòng giống hash và không có luồng tên export → hash, nên chưa phải API hashing.

## Vị trí tên hằng trong B2

| RVA lời gọi | Lệnh | Quan sát |
|---|---|---|
| 0x1064 | `call qword ptr [rip + 0xfa6]` | constant name 'CreateFileW' |
| 0x107B | `call qword ptr [rip + 0xf8f]` | constant name 'WriteFile' |
| 0x1092 | `call qword ptr [rip + 0xf78]` | constant name 'CloseHandle' |
