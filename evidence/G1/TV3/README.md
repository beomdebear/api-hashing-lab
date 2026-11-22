# G1-TV3-02 – Phân tích động B1 và B2

## 1. Thông tin nhiệm vụ

- **Đồ án:** API Hashing Lab
- **Thành viên:** TV3
- **Nhiệm vụ:** G1-TV3-02
- **Ngày thực nghiệm:** 22/11/2026
- **Môi trường phân tích:** Windows 11 x64 trên VMware
- **Công cụ:** Process Monitor, x64dbg, PowerShell

## 2. Mục tiêu

Thu thập dấu vết thực thi của hai mẫu:

- **B1:** Sử dụng API theo cơ chế import thông thường.
- **B2:** Tìm địa chỉ API trong lúc chạy thông qua `GetProcAddress` và tên API.

Mục tiêu chính là ghi nhận các lời gọi phân giải API, địa chỉ trả về và bằng chứng sử dụng con trỏ hàm.

## 3. Thông tin binary

Hai mẫu được biên dịch bằng MSVC x64 trên Windows host và chuyển sang Windows VM để phân tích.

| Mẫu | Build ID | Correctness trên host |
|---|---|---|
| B1 | 20261122-173007-790 | PASS |
| B2 | 20261122-173128-341 | PASS |

**SHA-256 B1:**

`E6278FF506CC69CCACA40FCF0A67BAC369540213B4B7422C7843E22FDF2EDFAC`

**SHA-256 B2:**

`6AB1B272F73766EEA3DB8015EBDA6CEF2D4698CDA1198AC4D29829706317FF09`

Cần đối chiếu SHA-256 của hai binary trong VM với các giá trị trên trước khi sử dụng kết quả thực nghiệm.

## 4. Phân tích B1

Đã thực hiện thử nghiệm B1 bằng Process Monitor và lưu các ảnh:

- `B1_createfile.png`
- `B1_writefile.png`
- `powershell_create_file.png`

Các ảnh phục vụ kiểm tra hoạt động file của B1. File PML gốc và chi tiết PID, timestamp cần được xác minh bổ sung.

## 5. Phân tích B2

### 5.1. Quan sát GetProcAddress

Trong phiên debug PID 8560, đã quan sát B2 gọi `GetProcAddress` để tìm các API:

- `CreateFileW`
- `WriteFile`
- `CloseHandle`

Khi hàm trả về, đã ghi nhận giá trị RAX tương ứng.

### 5.2. Kết quả API Resolution

| API | Địa chỉ trả về | Module | RVA |
|---|---|---|---|
| CreateFileW | 0x00007FF8253170B0 | kernel32.dll | 0x570B0 |
| WriteFile | 0x00007FF825317580 | kernel32.dll | 0x57580 |
| CloseHandle | 0x00007FF825316E00 | kernel32.dll | 0x56E00 |

**Module base:** `0x00007FF8252C0000`

Công thức:

`RVA = API Address - Module Base`

Các địa chỉ trên thuộc phiên debug được ghi nhận, không mặc định giữ nguyên trong những lần chạy khác do ASLR.

### 5.3. Bằng chứng gọi API gián tiếp

Trong phiên debug PID 8088, đã quan sát:

- B2 chạy đến lệnh `call qword ptr [rsp+68]`.
- Đích gọi được xác định là `kernel32.CreateFileW`.
- Khi Step Into bằng F7, RIP chuyển đến địa chỉ `CreateFileW`.

Hai API còn lại có kết quả phân giải địa chỉ nhưng chưa có bằng chứng Step Into tại call target.

| API | Resolution | Indirect call |
|---|---|---|
| CreateFileW | Đã quan sát | Đã xác minh |
| WriteFile | Đã quan sát | Chưa xác minh |
| CloseHandle | Đã quan sát | Chưa xác minh |

Không kết luận rằng hai API cuối không được gọi; chỉ xác định rằng chưa thu được minh chứng thực thi trực tiếp.

## 6. Danh sách minh chứng

Các ảnh được lưu trong cùng thư mục với README:

- `B1_createfile.png`
- `B1_writefile.png`
- `B2_createfile.png`
- `B2_writefile.png`
- `powershell_create_file.png`
- `powershell_create_file_b2.png`
- `B2_CreateFileW_return.png`
- `B2_WriteFile_argument.png`
- `B2_WriteFile_return.png`
- `B2_CloseHandle_return.png`
- `B2_kernel32_module_map.png`
- `B2_CreateFileW_indirect_call.png`
- `B2_CreateFileW_call_target.png`

## 7. Giới hạn

1. Correctness được xác nhận trên host; các phiên debugger thực hiện trên VM.
2. Chưa xác minh trực tiếp call target của WriteFile và CloseHandle.
3. Có phiên B2 kết thúc với exit code 30, tương ứng lỗi tạo file marker.
4. Minh chứng Procmon PML gốc cần kiểm tra và bổ sung nếu còn.
5. Cần giữ riêng PID, timestamp và địa chỉ của từng phiên debug.

## 8. Kết luận

TV3 đã thu được bằng chứng động về cơ chế phân giải API theo tên của B2, gồm tên API, địa chỉ trả về, module và RVA.

Đã xác minh luồng gọi gián tiếp đối với `CreateFileW`. Các bằng chứng chưa thu được được ghi rõ để nhóm tiếp tục kiểm tra nếu cần.

Kết quả này phục vụ việc so sánh B1/B2 và bàn giao dữ liệu runtime cho TV4.