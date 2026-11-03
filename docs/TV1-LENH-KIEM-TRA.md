# TV1 — Lệnh kiểm tra B1, B2, P1

## Môi trường

Mở x64 Native Tools Command Prompt for Visual Studio, nhập:

```text
powershell -NoProfile
```

Chuyển đến repo và kiểm tra:

```powershell
cd C:\Users\quyng\Downloads\api-hashing-lab
Get-Command cl.exe
$env:VSCMD_ARG_TGT_ARCH
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Kiến trúc phải là x64. Checker sử dụng bản v2: direct .NET Process.

## Các bản build đã kiểm tra

```powershell
$buildB1 = 'C:\Users\quyng\Downloads\api-hashing-lab\artifacts\builds\tv1\20261102-071051-495'
$buildB2 = 'C:\Users\quyng\Downloads\api-hashing-lab\artifacts\builds\tv1\20261103-075931-423'
$buildP1 = 'C:\Users\quyng\Downloads\api-hashing-lab\artifacts\builds\tv1\20261103-081901-822'
$audit = 'C:\Users\quyng\Downloads\api-hashing-lab\artifacts\builds\tv1\20261103-082456-391'
```

Các đường dẫn trên thuộc máy thực nghiệm. Nếu build lại hoặc chạy trên
máy khác, thay bằng BUILD DIRECTORY thực tế của từng lần build.

## Build lại khi cần

```powershell
.\scripts\tv1-build.ps1 -Sample B1
.\scripts\tv1-build.ps1 -Sample B2
.\scripts\tv1-build.ps1 -Sample P1
.\scripts\tv1-build.ps1 -Audit
```

Sau khi build lại, cập nhật các biến đường dẫn trước khi kiểm tra.

## Kiểm tra correctness

```powershell
.\scripts\tv1-check.ps1 -BuildDir $buildB1 -Sample B1
.\scripts\tv1-check.ps1 -BuildDir $buildB2 -Sample B2
.\scripts\tv1-check.ps1 -BuildDir $buildP1 -Sample P1
```

Cả ba mẫu đã đạt:
correctness_pass=True ; exit=0 ; marker=True.

Các thư mục run đã xác nhận:

- B1: artifacts/runs/tv1/20261102-071845-521
- B2: artifacts/runs/tv1/20261103-080051-392
- P1: artifacts/runs/tv1/20261103-081929-608

Mỗi lần kiểm tra mới sẽ tạo một thư mục run mới.
Correctness kiểm tra mã thoát và nội dung marker, chưa thu API trace độc lập.

## So sánh imports B1 và B2

```powershell
dumpbin /imports "$buildB1\B1\B1.exe" |
    Set-Content "$buildB1\B1\imports.txt"

dumpbin /imports "$buildB2\B2\B2.exe" |
    Set-Content "$buildB2\B2\imports.txt"

Select-String -Path "$buildB1\B1\imports.txt" -Pattern 'CreateFileW|WriteFile|CloseHandle|LoadLibraryW|GetProcAddress'
Select-String -Path "$buildB2\B2\imports.txt" -Pattern 'CreateFileW|WriteFile|CloseHandle|LoadLibraryW|GetProcAddress'
```

Kết quả đã quan sát trong các bản build này:

- B1: có CreateFileW, WriteFile, CloseHandle trong imports.
- B2: có LoadLibraryW, GetProcAddress; không thấy ba API đích trong kết quả lọc.
- B2 phân giải API theo tên, chưa sử dụng API hashing.

## Audit resolver DJB2 của P1

```powershell
& "$audit\audit-djb2\audit-djb2.exe" |
    Tee-Object -FilePath "$audit\audit-djb2.csv"

$auditExit = $LASTEXITCODE
Write-Host "Audit exit code: $auditExit"
```

Kết quả đã xác nhận:

| API | Hash | matches | name_equal | address_equal | status |
|---|---|---|---|---|---|
| CreateFileW | 0xEB96C610 | 1 | 1 | 1 | 0 |
| WriteFile | 0x663CECB0 | 1 | 1 | 1 | 0 |
| CloseHandle | 0x3870CA07 | 1 | 1 | 1 | 0 |

Audit exit code: 0.
Audit là kiểm tra nội bộ resolver, không phải API trace độc lập.

## Minh chứng cần giữ

- Source code và scripts đã dùng.
- build-manifest.csv: SHA256, compiler, cờ build.
- build.log và imports.txt.
- correctness-summary.csv và run-metadata.json.
- stdout, stderr, marker.txt của lần chạy thành công.
- audit-djb2.csv và ảnh kết quả audit.

Giữ nguyên artifacts trên máy thực nghiệm.
Chép minh chứng cần bàn giao vào evidence; không đưa toàn bộ artifacts vào Git.
