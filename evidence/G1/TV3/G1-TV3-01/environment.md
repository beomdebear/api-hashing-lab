<<<<<<< Updated upstream
# G1-TV3-01 – Môi trường thực nghiệm và thiết lập công cụ thu thập

## 1. Thông tin chung

| Thông tin | Nội dung |
|---|---|
| Đồ án | API Hashing Lab |
| Mã nhiệm vụ | G1-TV3-01 |
| Thành viên thực hiện | TV3 |
| Vai trò | Phân tích động và thu thập bằng chứng bộ nhớ |
| Giai đoạn | Giai đoạn 1 – Chuẩn bị môi trường |
| Ngày thực nghiệm | 31/10/2026 |
| Trạng thái | Đã thử nghiệm công cụ; đang hoàn thiện minh chứng |

### Mục tiêu

Thiết lập môi trường phân tích động trên máy ảo Windows và kiểm tra khả năng thu thập thông tin tiến trình, module, hoạt động hệ thống file và trạng thái thực thi của chương trình.

Đây là bước chuẩn bị trước khi phân tích các mẫu B1, B2 và P1 của nhóm.

## 2. Môi trường máy ảo

| Thành phần | Cấu hình |
|---|---|
| Phần mềm ảo hóa | VMware Workstation Pro 25H2 |
| Hệ điều hành | Windows 11 x64 |
| Windows Build | 26100 (theo thông tin phiên bản PowerShell quan sát được) |
| RAM | 8 GB |
| CPU | 2 bộ xử lý ảo |
| Ổ cứng | 80 GB |
| VMware Tools | Đã cài đặt |
| Snapshot | Đã tạo, cần xác nhận tên |
| Network Adapter | NAT khi cài đặt công cụ; trạng thái ngắt mạng cần xác nhận |

Máy ảo được sử dụng để thực hiện các thí nghiệm trong môi trường kiểm soát. Trước khi chạy mẫu đồ án, cần ngắt kết nối mạng và sử dụng snapshot phù hợp.

## 3. Các công cụ phân tích

### 3.1. Process Monitor (Procmon)

**Thông tin công cụ**

- Nhà phát triển: Microsoft Sysinternals
- Phiên bản: Chưa ghi nhận
- Chức năng: Theo dõi hoạt động hệ thống file, Registry, process và thread.

**Thực nghiệm**

Sử dụng PowerShell để tạo file văn bản trong thư mục thực nghiệm, đồng thời dùng Procmon thu thập sự kiện liên quan.

Kết quả quan sát:

| Trường | Giá trị |
|---|---|
| Process Name | powershell.exe |
| PID | 5400 |
| Operation | WriteFile |
| Result | SUCCESS |
| Path | C:\APIHashingLab\samples\test.txt |
| Offset | 0 |
| Length | 11 bytes |
| Thread ID | 10036 |
| Timestamp | 31/10/2026 08:23:30 |

**Nhận xét**

Procmon ghi nhận thành công sự kiện `WriteFile` của tiến trình PowerShell.

- `WriteFile`: Thao tác ghi dữ liệu vào file.
- `SUCCESS`: Thao tác ghi được hệ thống báo thành công.
- `Offset = 0`: Vị trí bắt đầu ghi là byte đầu tiên của file.
- `Length = 11`: Kích thước dữ liệu ghi là 11 byte.

Kết quả chứng minh khả năng thu thập dấu vết hoạt động hệ thống file bằng Procmon.

**Giới hạn**

Procmon không cung cấp đầy đủ thông tin về lời gọi `GetProcAddress`, giá trị địa chỉ trả về và việc thực thi API đã resolve. Do đó, cần kết hợp debugger hoặc collector chuyên dụng trong các giai đoạn tiếp theo.

### 3.2. Process Explorer

**Thông tin công cụ**

- Nhà phát triển: Microsoft Sysinternals
- Phiên bản: Chưa ghi nhận
- Chức năng: Quan sát cây tiến trình, PID, tiến trình cha và các DLL được nạp.

**Thực nghiệm**

Quan sát tiến trình PowerShell và kiểm tra thông tin module `kernel32.dll`.

Thông tin tiến trình:

| Trường | Giá trị |
|---|---|
| Process Name | powershell.exe |
| PID | 5400 |
| Parent PID | 9028 |
| Kiến trúc | 64-bit |

Thông tin module:

| Trường | Giá trị |
|---|---|
| Module | kernel32.dll |
| Description | Windows NT BASE API Client DLL |
| Version | 10.0.26100.9444 |
| Path | C:\Windows\System32\kernel32.dll |
| Load Address | 0x00007FFFF4080000 |
| Architecture | x64 |

**Nhận xét**

Process Explorer cho phép xác định các DLL được nạp trong không gian địa chỉ của một tiến trình.

Load Address là địa chỉ cơ sở của module trong lần quan sát. Đây là thông tin cần thiết để xác định địa chỉ tương đối RVA của một vị trí nằm trong module.

Công thức:

`RVA = Địa chỉ cần xét - Base Address của module`

**Giới hạn**

Việc một DLL xuất hiện trong danh sách module không chứng minh rằng một API cụ thể trong DLL đó đã được gọi.

### 3.3. x64dbg

**Thông tin công cụ**

- Công cụ: x64dbg
- Phiên bản: Chưa ghi nhận
- Kiến trúc: x64
- Chức năng: Debug chương trình, quan sát instruction, thanh ghi CPU, stack và bộ nhớ.

**Thực nghiệm**

Thông tin từ phiên debug đã ghi nhận:

| Trường | Giá trị |
|---|---|
| Tiêu đề phiên debug | qmodule-2.0-0.dll |
| PID | 1320 |
| Main Thread ID | 6296 |
| Module đang quan sát | ntdll.dll |
| RIP | 0x00007FFFF554223A |
| Trạng thái | Paused – System breakpoint reached |

**Các nội dung đã quan sát**

1. Giao diện CPU và các lệnh Assembly.
2. Các thanh ghi như RAX, RBX, RCX, RDX, RSP và RIP.
3. Trạng thái chương trình tạm dừng tại system breakpoint.
4. Bảng Memory Map.
5. Các vùng bộ nhớ liên quan đến stack, heap và module.

**Nhận xét**

x64dbg cho phép quan sát trạng thái thực thi và thông tin bộ nhớ của tiến trình.

Thanh ghi RIP cho biết địa chỉ instruction tiếp theo sẽ được thực thi. Memory Map cho biết các vùng bộ nhớ được ánh xạ, quyền truy cập và module liên quan.

**Giới hạn**

Phiên debug hiện tại chỉ dùng để kiểm tra công cụ. Chưa có bằng chứng về quá trình API hashing hoặc API resolution của các mẫu B1, B2, P1.

## 4. Tổng hợp kết quả

| Nội dung kiểm tra | Kết quả |
|---|---|
| Thu thập thông tin process | Đã quan sát |
| Xác định PID và Parent PID | Đã quan sát |
| Quan sát DLL được nạp | Đã quan sát |
| Xác định module Load Address | Đã quan sát |
| Thu thập sự kiện WriteFile | Thành công |
| Quan sát debugger breakpoint | Thành công |
| Quan sát thanh ghi CPU | Thành công |
| Quan sát Memory Map | Thành công |
| Thu trace API resolution | Chưa thực hiện |
| Xác nhận API đã resolve được sử dụng | Chưa thực hiện |

## 5. Minh chứng thực nghiệm

Các ảnh minh chứng đã được đưa vào thư mục `evidence` của repository cục bộ và push lên GitHub trong branch của TV3.

Thư mục lưu trữ:

`evidence/G1/TV3/G1-TV3-01/`

**Danh sách minh chứng hiện có**

1. Ảnh Procmon – Thông tin tiến trình PowerShell.
2. Ảnh Procmon – Sự kiện WriteFile thành công.
3. Ảnh Process Explorer – Thông tin module kernel32.dll.
4. Ảnh x64dbg – Giao diện CPU và Registers.
5. Ảnh x64dbg – Memory Map.

**Minh chứng và thông tin cần bổ sung**

- File trace gốc định dạng `.PML`, nếu còn hoặc thu lại trong lần chạy mới.
- Ảnh cấu hình VMware và snapshot.
- Phiên bản chính xác của các công cụ.
- Tình trạng ngắt kết nối mạng trước thực nghiệm.
- Xác nhận review và merge các minh chứng vào branch `dev`.

## 6. Công việc tiếp theo

- Hoàn thiện README hướng dẫn tái lập.
- Kiểm tra và bổ sung các minh chứng còn thiếu.
- Nhận mẫu B1/B2 từ TV1.
- Thu thập trace runtime của B1/B2.
- Phát triển dữ liệu module map và các trường telemetry phục vụ D1.

## 7. Kết luận

Môi trường phân tích động Windows 11 VM đã được thiết lập và các công cụ Process Monitor, Process Explorer, x64dbg đã được thử nghiệm bước đầu.

Kết quả cho thấy có thể thu thập thông tin về process, module, thao tác file và trạng thái debugger.

Đây là cơ sở để tiếp tục thu thập bằng chứng API resolution trên các mẫu thực nghiệm của nhóm. Chưa thể kết luận về sự xuất hiện của API hashing từ các thử nghiệm hiện tại.
=======
# G1-TV3-01 – Analysis Environment

## 1. General Information

- **Project:** API Hashing Lab
- **Task ID:** G1-TV3-01
- **Member:** TV3
- **Role:** Dynamic Analysis & Memory Evidence
- **Phase:** 1 – Environment Setup and Initial Collection
- **Test Date:** 2026-10-31
- **Status:** Initial tool testing completed; evidence packaging pending

## 2. Virtual Machine Environment

| Component | Configuration |
|---|---|
| Hypervisor | VMware Workstation Pro 25H2 |
| Guest OS | Windows 11 x64 |
| Windows Build | 26100 (observed from PowerShell version) |
| RAM | 8 GB |
| CPU | 2 virtual processors |
| Virtual Disk | 80 GB |
| VMware Tools | Installed |
| Snapshot | Created (name to be confirmed) |
| Network Adapter | NAT during installation; isolation status to be confirmed |

The virtual machine is used to perform controlled runtime analysis. Network connectivity will be disabled before executing project samples.

## 3. Analysis Tools

### 3.1. Process Monitor (Procmon)

- **Developer:** Microsoft Sysinternals
- **Version:** To be updated
- **Purpose:** Collect file-system, Registry, process and thread activity.

**Test information:**

- Process: `powershell.exe`
- PID: `5400`
- Operation: `WriteFile`
- Result: `SUCCESS`
- Target: `C:\APIHashingLab\samples\test.txt`
- Offset: `0`
- Length: `11 bytes`
- Timestamp: `2026-10-31 08:23:30`

**Observed result:** Successfully captured a file-write operation performed by PowerShell.

**Limitation:** Procmon does not directly provide a complete trace of dynamic API resolution or API return addresses.

### 3.2. Process Explorer

- **Developer:** Microsoft Sysinternals
- **Version:** To be updated
- **Purpose:** Inspect running processes, process hierarchy and loaded modules.

**Test information:**

- Process: `powershell.exe`
- PID: `5400`
- Parent PID: `9028`
- Observed module: `kernel32.dll`
- Module path: `C:\Windows\System32\kernel32.dll`
- Module version: `10.0.26100.9444`
- Load address: `0x00007FFFF4080000`
- Architecture: x64

**Observed result:** Successfully inspected process information and the base address of a loaded DLL.

**Limitation:** Loaded-module information does not establish whether a particular API has been called.

### 3.3. x64dbg

- **Tool:** x64dbg
- **Version:** To be updated
- **Architecture:** x64
- **Purpose:** Debug process execution and inspect registers, memory and loaded modules.

**Test information:**

- Debugging session title: `qmodule-2.0-0.dll`
- Observed PID: `1320`
- Main thread ID: `6296`
- Observed module: `ntdll.dll`
- RIP: `0x00007FFFF554223A`
- Status: `Paused – System breakpoint reached`

**Observed result:**
- Opened a debugging session.
- Inspected CPU instructions and registers.
- Viewed the Memory Map.
- Observed a system breakpoint.

**Limitation:** API-resolution arguments, return addresses and subsequent API execution have not yet been collected for the project's B1/B2/P1 samples.

## 4. Preliminary Collection Results

| Observation | Status |
|---|---|
| Process information | Observed |
| Process ID and parent PID | Observed |
| Loaded DLL information | Observed |
| Module base address | Observed |
| File-system WriteFile event | Observed |
| Debugger breakpoint | Observed |
| Memory Map | Observed |
| API resolution trace | Not yet tested |
| Resolved API execution | Not yet tested |

## 5. Evidence Status

Screenshots of the preliminary tests are currently stored outside the repository and will be added later.

Planned evidence directory:

`evidence/G1/TV3/G1-TV3-01/`

Expected evidence:
- VMware configuration and snapshot screenshots
- Procmon WriteFile event screenshot
- Process Explorer process/module screenshots
- x64dbg CPU and Memory Map screenshots
- Native collector logs, when exported

No evidence files are claimed to be committed at this stage.

## 6. Next Steps

- Confirm the installed tool versions.
- Export and organize collector logs.
- Add screenshots and original logs to the evidence directory.
- Test collection procedures using B1 and B2.
- Document collector coverage and missing telemetry.

## 7. Conclusion

The initial Windows 11 analysis environment has been prepared, and Process Monitor, Process Explorer and x64dbg have been tested.

Preliminary process, module, file-system and debugger observations were obtained. Further collection is required to capture dynamic API resolution and establish links between resolved addresses and subsequent API calls.
>>>>>>> Stashed changes
