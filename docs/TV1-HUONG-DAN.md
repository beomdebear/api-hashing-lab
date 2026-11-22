# Hướng dẫn hoàn thành TV1

Bạn phụ trách mẫu PoC, tính đúng của cơ chế tìm API, biến thể và giải thích cách hoạt động.
Không cần tự viết detector thay TV2/TV4. Hoàn thành TV1 nghĩa là có source, binary, log kiểm tra,
minh chứng và phần báo cáo; không chỉ chạy được file exe.

## 1 Chuẩn bị môi trường và nhánh làm việc

Thực hiện build và chạy trong Windows VM x64 của nhóm. Có thể soạn source bằng VS Code ở máy chính.
Cài công cụ khi VM còn Internet, chốt snapshot rồi ngắt Internet khi chạy thực nghiệm.

Cần có:
- Visual Studio hoặc Build Tools, chọn workload Desktop development with C++ và Windows SDK.
- Git; VS Code nếu cần chỉnh sửa. Python 3 chỉ cần khi tính lại hash, không cần để build bộ có sẵn.
- Thư mục repo ngắn, ví dụ `C:\Lab\api-hashing-lab`.

Mở **x64 Native Tools Command Prompt for Visual Studio**, gõ `powershell -NoProfile`.
Các lệnh tiếp theo dùng PowerShell trong cửa sổ đó để giữ môi trường compiler x64.

```powershell
cd C:\Lab\api-hashing-lab
Get-Command cl.exe
$env:VSCMD_ARG_TGT_ARCH
git status
git switch -c tv1/poc
```

Nếu nhánh đã có, dùng `git switch tv1/poc`. Nếu chưa cài Git trong VM, có thể build source đã chép
vào VM trước và quản lý commit trên máy chính. Không cần quyền Administrator để chạy mẫu.

Ghi Windows build, kiến trúc, compiler, SDK, ngày và tên snapshot vào `docs/environment.md` hiện có.
Không thay nội dung của các thành viên khác. Chụp ảnh công cụ x64 và snapshot sạch.

Nếu PowerShell báo script bị chặn bởi execution policy, trong cửa sổ lab này dùng:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Nếu file tải về vẫn bị chặn, xem nội dung rồi bỏ dấu chặn cho đúng hai script:
```powershell
Unblock-File .\scripts\tv1-build.ps1
Unblock-File .\scripts\tv1-check.ps1
```
Không đổi chính sách toàn máy. Nếu Group Policy chặn, ghi nhận lỗi và trao đổi với người quản lý lab.

Minh chứng: `evidence/G1/TV1/G1-TV1-01/` gồm ảnh VM/snapshot, thông tin môi trường và README.

## 2 Làm B1 và B2 trước

Đọc `samples/benign/B1_static_import/main.c`, B2 và `samples/common/tv1_program.h`.
`TV1_MODE=0` gọi CreateFileW/WriteFile/CloseHandle trực tiếp.
`TV1_MODE=1` dùng LoadLibraryW/GetProcAddress với tên rõ, kiểm tra con trỏ rồi gọi.

Build B1:
```powershell
.\scripts\tv1-build.ps1 -Sample B1
```
Script in `BUILD DIRECTORY: ...`. Gán đúng đường dẫn vừa in, không dùng dấu chấm giả bên dưới:
```powershell
$build = 'C:\Lab\api-hashing-lab\artifacts\builds\tv1\THAY-BANG-BUILD-ID'
.\scripts\tv1-check.ps1 -BuildDir $build -Sample B1
```
Làm tương tự với B2 bằng `-Sample B2` và cập nhật `$build` theo thư mục mới.
Kết quả mong đợi: `correctness_pass=True`, exit 0, marker có đúng `D08 LAB MARKER` và CRLF.
Script ghi `RUN DIRECTORY`, mở thư mục đó để chụp log và marker thật.

Kiểm tra imports bằng công cụ đi cùng MSVC:
```powershell
dumpbin /imports "$build\B2\B2.exe" | Set-Content "$build\B2\imports.txt"
```
Với B1, đổi đường dẫn đúng build/B1. Cùng TV2 đối chiếu imports/strings trong Ghidra.
Không suy ra từ source rằng binary chắc chắn sạch tên API: CRT và linker có thể thêm imports.
Nếu API mục tiêu vẫn có trong imports của B2/P1, ghi lại và tìm nguồn; chưa được tuyên bố đã che tên.

Minh chứng: `evidence/G1/TV1/G1-TV1-02/` gồm build.log, SHA-256, imports, stdout,
run-metadata.json, marker và ảnh. Source chỉ cần đường dẫn + commit, không sao chép vào evidence.

## 3 Làm P1 và hiểu từng bước

Đọc theo thứ tự:
1. `P1_djb2/main.c`: thuật toán 1, seed 5381 và ba hằng số hash đã tính trước.
2. `tv1_hash.h`: h bắt đầu từ seed; mỗi byte tên cập nhật h = h * 33 + byte, giới hạn 32 bit.
3. `tv1_resolver.h`: lấy danh sách tên export từ kernel32.dll đang được nạp.
4. `tv1_find_name`: hash từng tên, đếm tất cả tên khớp; 0 tên là thiếu, hơn 1 tên là collision.
5. `tv1_resolve`: truyền tên tìm được cho GetProcAddress để lấy địa chỉ thật.
6. `tv1_program.h`: kiểm tra đủ ba địa chỉ, rồi tạo file, ghi marker và đóng handle.

GetProcAddress nhận TÊN, không nhận hash. Tên được lấy từ DLL khi chạy, không cần nhúng tên
mục tiêu dưới dạng chuỗi trong nhánh hashing. Tên vẫn có thể quan sát được lúc chạy.
Windows xử lý forwarded exports qua GetProcAddress; địa chỉ trả về có thể thuộc KernelBase,
không nhất thiết ở kernel32. Không tính RVA bằng cách luôn trừ base kernel32.

Build/chạy P1:
```powershell
.\scripts\tv1-build.ps1 -Sample P1
# Cập nhật $build bằng BUILD DIRECTORY vừa in
.\scripts\tv1-check.ps1 -BuildDir $build -Sample P1
```

Kiểm tra tính đúng của tên và địa chỉ bằng công cụ tách riêng:
```powershell
.\scripts\tv1-build.ps1 -Audit
# Gán thư mục BUILD DIRECTORY của lần audit vào $audit
$audit = 'C:\Lab\api-hashing-lab\artifacts\builds\tv1\THAY-BANG-AUDIT-BUILD-ID'
& "$audit\audit-djb2\audit-djb2.exe" | Tee-Object "$audit\audit-djb2.csv"
$LASTEXITCODE
```
Mỗi API cần matches=1, name_equal=1, address_equal=1, status=0; mã thoát toàn công cụ là 0.
Audit so kết quả resolver với GetProcAddress bằng tên rõ. Không đưa audit.exe, log audit hoặc
source vào dữ liệu đầu vào detector; đây là đáp án kiểm chứng riêng của TV1.

Minh chứng: `evidence/G1/TV1/G1-TV1-03/`: kết quả audit, hash-values, build/run logs, marker;
cùng TV2 chụp vòng hash/so sánh, cùng TV3 thu trace độc lập. Log tự ghi không chứng minh detector đúng.

## 4 Hoàn thành P2 và P3

P2 dùng FNV-1a 32 bit: XOR byte trước, nhân 16777619 sau; seed 2166136261.
P3 dùng CRC32 phản chiếu: polynomial 0xEDB88320, khởi tạo 0xFFFFFFFF, XOR cuối 0xFFFFFFFF.
Không tính byte NUL kết thúc tên; tên phân biệt chữ hoa/thường; tính đúng phiên bản API W.

Build/chạy từng mẫu như P1 và chạy hai audit:
```powershell
& "$audit\audit-fnv1a\audit-fnv1a.exe" | Tee-Object "$audit\audit-fnv1a.csv"
$LASTEXITCODE
& "$audit\audit-crc32\audit-crc32.exe" | Tee-Object "$audit\audit-crc32.csv"
$LASTEXITCODE
```

P1/P2/P3 phải có cùng marker, cùng API mục tiêu và cùng cấu hình compiler.
Khác biệt chủ yếu cần kiểm tra là thuật toán và hằng số hash.
Minh chứng: `evidence/G2/TV1/G2-TV1-01/` với source commit, bảng hash, audit, log và marker.

## 5 Hoàn thành P4 và P5

P4 lấy P1 làm gốc, đổi seed 5381 thành 1337 và tính lại cả ba hash mục tiêu.
P5 lấy P1 làm gốc, giữ seed/hash, đổi thứ tự tìm địa chỉ từ create/write/close thành write/close/create.
Thứ tự THỰC HIỆN vẫn phải tạo file → ghi → đóng.

```powershell
& "$audit\audit-seed1337\audit-seed1337.exe" | Tee-Object "$audit\audit-seed1337.csv"
$LASTEXITCODE
```

Nếu bạn chỉnh thuật toán/seed, sửa công thức/cấu hình tương ứng trong
`scripts/tv1-generate-hashes.py` và `tv1_hash.h`, rồi chạy `python scripts/tv1-generate-hashes.py`.
Lệnh này tạo lại 9 main.c; hãy commit hoặc sao lưu phần sửa tay trước khi chạy.
Không chỉ đổi seed trong C mà giữ hash mục tiêu cũ.

Nhờ TV3 xác nhận thứ tự resolve của P5 bằng collector/debugger. Marker giống nhau chỉ xác nhận tác vụ,
không chứng minh thứ tự resolve đã khác.

## 6 Làm E1 và E2

E1 đổi bit cao của hash CreateFileW rồi thử resolve; nếu không tìm được, thoát 10, không marker.
Nếu hash sai tình cờ trùng một export trên bản Windows khác, mẫu không gọi địa chỉ đó và thoát 21:
đó là fixture chưa phù hợp, không được sửa báo cáo thành PASS.

E2 mặc định thoát 20 trước khi resolve, không marker. Nhánh `--continue` giữ đường hash có thể chạy
trong binary, nhưng KHÔNG truyền tham số đó cho thí nghiệm E2 mặc định.
E1/E2 vẫn là mẫu có mã liên quan API hashing; hành vi không hoàn tất không tự biến nhãn thành benign.

Minh chứng P4/P5/E1/E2: `evidence/G2/TV1/G2-TV1-02/` gồm bảng khác biệt, log, mã thoát,
SHA-256; ảnh marker của P4/P5 và thư mục chạy mới không marker của E1/E2.

## 7 Kiểm tra toàn bộ và bàn giao cuối tuần 7

```powershell
.\scripts\tv1-build.ps1 -Sample All
# Cập nhật $build theo BUILD DIRECTORY mới
.\scripts\tv1-check.ps1 -BuildDir $build -Sample All -Repeat 3
```

| Mẫu | Exit mong đợi | Marker |
|---|---:|---|
| B1 B2 P1 P2 P3 P4 P5 | 0 | Có, đúng 16 byte |
| E1 | 10 | Không |
| E2 | 20 | Không |

Ba lần chạy mỗi binary để kiểm tra tính ổn định, không tính thành ba mẫu độc lập.
`correctness_pass=True` của E1/E2 nghĩa là mẫu lỗi diễn ra đúng dự kiến, không phải tạo marker thành công.

Kiểm tra bổ sung: chạy một mẫu thành công lần nữa trong CHÍNH thư mục run trước đó.
Vì marker đã có, phải trả 30 và giữ file cũ. Chụp/log riêng, không sửa run-metadata của lần đầu.
Đây là kiểm tra không ghi đè; không đưa lần chạy này vào bộ đánh giá chuẩn.

Gửi TV2 source commit + binary/SHA-256 để phân tích; gửi TV3 cùng binary và cách chạy;
gửi TV4 build-manifest.csv, cấu hình, bảng biến thể, kết quả correctness, audit và các lỗi đã biết.
TV4 bổ sung nhãn/split trong manifest chung; TV1 không tự đổi nhãn khi detector cho kết quả khác.

Minh chứng: `evidence/G2/TV1/G2-TV1-03/`. Chốt commit/tag cùng nhóm trước test tuần 8.
Tập test phải được nhóm thống nhất trước khi chỉnh detector; không dùng toàn bộ biến thể để tuning.
Kiểm tra correctness riêng của TV1 không phải hoạt động tuning detector.

## 8 Điều tra lỗi tuần 8

Phân biệt: lỗi mẫu không tạo marker đúng; collector không thu được dữ liệu; detector dự đoán sai.
Với mỗi lỗi: ghi sample_id, SHA-256, run_id, hiện tượng, bước tái hiện, nguyên nhân và cách xử lý.
Nếu sửa source làm đổi binary, tạo build/phiên bản mới và báo TV4 chạy lại phần đánh giá bị ảnh hưởng.
Không trộn kết quả binary cũ và mới như cùng một mẫu không đổi.

Minh chứng: `evidence/G3/TV1/G3-TV1-01/`: bảng lỗi, log tái hiện, diff source và phiên bản liên quan.

## 9 Báo cáo và demo tuần 9

Viết 5 ý bằng lời của bạn: API hashing che thông tin gì; luồng B1/B2/P1 khác nhau thế nào;
hash mục tiêu được tính khi nào; resolver tìm địa chỉ như thế nào; mẫu xử lý lỗi ra sao.
Vẽ luồng bên trong PoC; lập bảng P1–P5 chỉ thay yếu tố nào. Minh họa bằng ảnh thực tế.

Demo theo thứ tự B1 → B2 → P1 → P4 hoặc P5 → E1/E2. Dùng chính binary đã chốt và
run directory mới. Chỉ nói kết quả detector mà TV2/TV4 thực sự đo được.

Minh chứng: `evidence/G3/TV1/G3-TV1-02/`: bản thảo phần PoC, sơ đồ, ảnh và video chạy thử.

## 10 Bàn giao tuần 10

Đối chiếu checklist trong `docs/TV1-CHECKLIST.md`. Cùng TV2 review phần cơ chế;
cùng TV3 kiểm tra đúng binary demo; cùng TV4 kiểm tra link source, build, log và minh chứng.
Minh chứng: `evidence/G3/TV1/G3-TV1-03/`: checklist, log build cuối, SHA-256 và bản báo cáo.

Commit source/config/docs/evidence đã kiểm tra; không commit artifacts nếu repo đã ignore thư mục đó.
Lưu gói binary/trace riêng theo quy định nhóm và ghi vị trí + checksum, không bỏ các file gốc.

## Mã thoát và xử lý nhanh

| Mã | Ý nghĩa |
|---:|---|
| 0 | Ghi và đóng marker thành công |
| 10 | Không có tên export khớp hash; chỉ mong đợi ở E1 |
| 11 | Nhiều tên khớp cùng hash; dừng thay vì chọn đại |
| 12 | Metadata PE không hợp lệ/không đúng phạm vi x64 của parser |
| 13 | GetProcAddress không lấy được địa chỉ |
| 14 | Không nạp được module |
| 20 | E2 dừng trước hành vi mục tiêu |
| 21 | Hash sai của E1 có kết quả bất ngờ; cần điều tra |
| 30 | Không tạo được marker; kiểm tra file đã tồn tại/quyền ghi |
| 31 | Ghi lỗi hoặc thiếu byte |
| 32 | Đóng handle thất bại |

`cl.exe not found`: dùng đúng developer shell, kiểm tra workload C++.
`VCRUNTIME... missing`: bản /MD cần runtime tương ứng; build và chạy trên VM đã cài công cụ,
hoặc cài Visual C++ Redistributable chính thức trước khi chốt snapshot.
Script không chạy: kiểm tra policy theo bước 1, không tắt bảo mật toàn máy.

## Giới hạn và nguồn tham khảo

Resolver chỉ đọc module kernel32 x64 đã được Windows nạp; không phải parser tổng quát cho file PE
không tin cậy. Không duyệt PEB, không chèn mã vào tiến trình khác, không cấp phát mã thực thi.
Lỗi phân tích/collector và imports từ CRT phải được ghi nhận trong báo cáo.

- Microsoft, GetProcAddress: https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress
- Microsoft, PE format: https://learn.microsoft.com/en-us/windows/win32/debug/pe-format
- Microsoft, CreateFileW: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
- Microsoft, MSVC command line: https://learn.microsoft.com/en-us/cpp/build/building-on-the-command-line
