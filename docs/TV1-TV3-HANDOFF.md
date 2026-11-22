# TV1 -> TV3: B1/B2/P1 handoff (Giai đoạn 1)

PR #3 đưa source, scripts, correctness và audit lên Git; không chứa binary. Chỉ chạy trong Windows VM cô lập, có snapshot, không kết nối Internet khi thực nghiệm.

## Binary gốc đã PASS trên Windows

| Sample | Build ID | SHA-256 |
|---|---|---|
| B1 | `20261102-071051-495` | `8BC030497FBF144C3A6A0BDA35EC8E474111686A687FD9A660B97B5DDE88F327` |
| B2 | `20261103-075931-423` | `546C2B771087AD12A470632AD6CA83B1960BCD4901D02DFD3EBAEFDBB22AB183` |
| P1 | `20261103-081901-822` | `DDFB2A2903D6D63C822831BF8650B57F56A2CAA710585154BF14DBE46E04B215` |

Mỗi mẫu hiện có 1 lần correctness PASS. Source commit đúng thời điểm build chưa xác minh.

## Phương án A: gửi chính binary gốc

Trên máy TV1, mở PowerShell tại gốc repo:

```powershell
$base = (Get-Location).Path
$dest = Join-Path $base 'artifacts/handoff/tv1-g1'
New-Item -ItemType Directory -Path $dest -Force | Out-Null
$builds = @{ B1='20261102-071051-495'; B2='20261103-075931-423'; P1='20261103-081901-822' }
foreach ($id in @('B1','B2','P1')) {
  $source = Join-Path $base "artifacts/builds/tv1/$($builds[$id])/$id/$id.exe"
  if (-not (Test-Path $source)) { throw "Missing original binary: $source" }
  Copy-Item -LiteralPath $source -Destination (Join-Path $dest "$id.exe")
}
Get-ChildItem $dest -Filter '*.exe' | Get-FileHash -Algorithm SHA256 | Format-Table Path, Hash
```

Đối chiếu **đủ 3 SHA-256** với bảng ở trên, dừng nếu khác. Chuyển 3 EXE cùng 3 manifest build gốc và build logs bằng kênh nội bộ cho TV3; TV3 tính lại SHA-256 khi nhận. Không commit toàn bộ `artifacts/` vào repo. Nếu muốn chỉ gửi qua Git, dùng Phương án B.

## Phương án B: TV3 tự build từ repo

TV3 lấy source nhánh `tv1` (trước khi merge), hoặc `dev` (sau khi merge). Mở x64 Native Tools Command Prompt for Visual Studio và gõ `powershell -NoProfile`. Trong gốc repo:

```powershell
Get-Command cl.exe
$env:VSCMD_ARG_TGT_ARCH
.\scripts\tv1-build.ps1 -Sample B1
.\scripts\tv1-build.ps1 -Sample B2
.\scripts\tv1-build.ps1 -Sample P1
```

Mỗi build in ra `BUILD DIRECTORY` và tạo `build-manifest.csv`. Với đường dẫn build mới tương ứng, chạy:

```powershell
.\scripts\tv1-check.ps1 -BuildDir 'DUONG_DAN_BUILD_B1_THUC_TE' -Sample B1
.\scripts\tv1-check.ps1 -BuildDir 'DUONG_DAN_BUILD_B2_THUC_TE' -Sample B2
.\scripts\tv1-check.ps1 -BuildDir 'DUONG_DAN_BUILD_P1_THUC_TE' -Sample P1
```

Lưu `run-metadata.json`, marker và correctness-summary.csv từ run mới. **Không dùng SHA, run ID hoặc correctness cũ để đại diện build mới**. Compiler/linker khác có thể tạo binary với SHA khác.

## TV3 thu trace độc lập

- B1: quan sát lời gọi API ghi marker thông thường.
- B2: quan sát nạp module, GetProcAddress theo tên và địa chỉ trả về.
- P1: đối chiếu resolution và indirect call với module map; việc xác định vòng hash cần phối hợp bằng chứng static (TV2).
- Ghi run_id, binary SHA-256, PID, thời gian, API/module, địa chỉ trả về, call target, module+RVA và collector_status; thiếu trường nào thì ghi rõ.
- `collector_status=not_collected` trong ba correctness CSV: **TV1 chưa thu independent dynamic API trace**.
- Không cho detector đọc audit CSV, source hay nhãn ground truth.

## Giới hạn

Cần xác nhận còn EXE, log và marker gốc trên máy TV1; Git không lưu `artifacts/`. Snapshot/Windows full build và SDK cần TV1 bổ sung minh chứng. Không coi correctness là detector result.
