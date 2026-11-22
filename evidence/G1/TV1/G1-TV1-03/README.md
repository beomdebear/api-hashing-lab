# Minh chứng G1-TV1-03 - P1 DJB2

**Trạng thái:** P1 correctness PASS (1 run) và audit DJB2 PASS; hồ sơ **chờ review**. Chưa có independent dynamic API trace.

- Người thực hiện: TV1; reviewer: TV2 (chưa phê duyệt), TV3 nhận mẫu để thu runtime trace.
- Source: `samples/api_hashing/P1_djb2/main.c`, `samples/common/tv1_hash.h`, `tv1_resolver.h`, `tv1_program.h`.
- Thuật toán: DJB2 32-bit, seed 5381; export name được băm và so sánh; sau đó GetProcAddress được gọi bằng **tên** vừa tìm.
- Source commit đúng thời điểm build: chưa xác minh; không gán commit PR cho binary cũ.

| Build ID | Run ID | SHA-256 P1.exe | Exit | Marker | Correctness |
|---|---|---|---|---|---|
| `20261103-081901-822` | `20261103-081929-608-P1-1` | `DDFB2A2903D6D63C822831BF8650B57F56A2CAA710585154BF14DBE46E04B215` | 0 | True / content_ok=True | True |

## Audit DJB2 (Windows VM)
- Audit build ID: `20261103-082456-391`.
- `audit-djb2.csv`: CreateFileW 0xEB96C610; WriteFile 0x663CECB0; CloseHandle 0x3870CA07.
- Cả 3 dòng: `matches=1`, `name_equal=1`, `address_equal=1`, `status=0`.
- Audit process exit=0 theo terminal đã lưu trong bàn giao TV1.
- Files đã commit: `P1-correctness-summary.csv`, `audit-djb2.csv`, `audit-build-manifest.csv`, `audit-djb2-build.log`.
- Manifest **audit** ghi MSVC compiler version 19.51.36260.0, kiến trúc x64, flags `/Od /MD /W4 /TC; no PDB`. Không suy ra version compiler chính xác của P1 trước khi đọc manifest P1.
- `matches=1` chỉ áp dụng cho ba hash mục tiêu trên module của lần kiểm tra; không chứng minh toàn bộ thuật toán không collision.

## Vị trí binary / log / marker trên VM
- P1 binary: `artifacts/builds/tv1/20261103-081901-822/P1/P1.exe`
- P1 build log: `artifacts/builds/tv1/20261103-081901-822/P1/build.log`
- P1 build manifest: `artifacts/builds/tv1/20261103-081901-822/build-manifest.csv`
- P1 run folder: `artifacts/runs/tv1/20261103-081929-608/20261103-081929-608-P1-1/` (`stdout.txt`, `stderr.txt`, `run-metadata.json`, `marker.txt`)
- P1 run summary: `artifacts/runs/tv1/20261103-081929-608/correctness-summary.csv`
- Audit binary: `artifacts/builds/tv1/20261103-082456-391/audit-djb2/audit-djb2.exe`.
- Audit CSV gốc: `artifacts/builds/tv1/20261103-082456-391/audit-djb2.csv`.

Đường dẫn trên suy ra từ ID thực và scripts; TV1 cần xác nhận còn file trên VM. `artifacts/` không push Git.

## Giới hạn và bàn giao
- P1 CSV ghi `collector_status=not_collected`: **chưa có trace API độc lập**, TV3 cần thực hiện.
- Chưa xác minh đầy đủ strings P1 trên binary, 3 repeats hoặc Windows build/snapshot.
- Audit kiểm correctness tên/địa chỉ, không được dùng làm detector input.
- Marker chuẩn là 16 byte ASCII `D08 LAB MARKER\r\n`.
- Hướng dẫn gửi binary hoặc rebuild: `docs/TV1-TV3-HANDOFF.md`.
