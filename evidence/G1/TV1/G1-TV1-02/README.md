# Minh chứng G1-TV1-02 - B1/B2

**Trạng thái:** Đã xác minh correctness trên Windows VM x64 (mỗi mẫu 1 lần); **chờ review** hồ sơ. Chưa có independent dynamic API trace.

- Người thực hiện: TV1; người review: TV2 (chưa phê duyệt).
- Mẫu: B1 static imports, B2 dynamic name via GetProcAddress.
- Cách build/check: `scripts/tv1-build.ps1`, `scripts/tv1-check.ps1` (checker v2 - direct .NET Process).
- Source commit: **chưa xác minh commit đúng thời điểm build**; các lần build diễn ra trước commit bộ kit.

| Sample | Build ID | Run ID | SHA-256 (.exe) | Exit | Marker | Correctness |
|---|---|---|---|---|---|---|
| B1 | `20261102-071051-495` | `20261102-071845-521-B1-1` | `8BC030497FBF144C3A6A0BDA35EC8E474111686A687FD9A660B97B5DDE88F327` | 0 | True / content_ok=True | True |
| B2 | `20261103-075931-423` | `20261103-080051-392-B2-1` | `546C2B771087AD12A470632AD6CA83B1960BCD4901D02DFD3EBAEFDBB22AB183` | 0 | True / content_ok=True | True |

## Evidence đã commit
- `B1-correctness-summary.csv`, `B2-correctness-summary.csv`: exit=0, timeout=False, marker đúng nội dung.
- Đã đối chiếu imports qua dumpbin trong lần làm trước: B1 có CreateFileW, WriteFile, CloseHandle; B2 có LoadLibraryW và GetProcAddress. Ảnh/log gốc imports cần bổ sung nếu reviewer yêu cầu.

## Vị trí log / marker thực tế trên VM (không commit trong Git)
Gốc repo: `C:\Users\quyng\Downloads\api-hashing-lab`.
- B1 binary: `artifacts/builds/tv1/20261102-071051-495/B1/B1.exe`
- B1 build log: `artifacts/builds/tv1/20261102-071051-495/B1/build.log`
- B1 manifest: `artifacts/builds/tv1/20261102-071051-495/build-manifest.csv`
- B1 run folder: `artifacts/runs/tv1/20261102-071845-521/20261102-071845-521-B1-1/`: `stdout.txt`, `stderr.txt`, `run-metadata.json`, `marker.txt`
- B1 run summary: `artifacts/runs/tv1/20261102-071845-521/correctness-summary.csv`
- B2 binary: `artifacts/builds/tv1/20261103-075931-423/B2/B2.exe`
- B2 build log: `artifacts/builds/tv1/20261103-075931-423/B2/build.log`
- B2 manifest: `artifacts/builds/tv1/20261103-075931-423/build-manifest.csv`
- B2 run folder: `artifacts/runs/tv1/20261103-080051-392/20261103-080051-392-B2-1/`: `stdout.txt`, `stderr.txt`, `run-metadata.json`, `marker.txt`
- B2 run summary: `artifacts/runs/tv1/20261103-080051-392/correctness-summary.csv`

Các đường dẫn trên được dựng từ build/run ID thực trong CSV và script checker v2. TV1 phải đối chiếu file thật trên VM; **chưa xác nhận toàn bộ artifacts còn tồn tại**.

## Giới hạn và TV3
- `collector_status=not_collected` trong CSV: correctness không phải dynamic API trace.
- TV3 phải tự ghi API trace/module map; xem `docs/TV1-TV3-HANDOFF.md`.
- Chưa xác minh Windows full build, snapshot, 3 repeats, và strings đầy đủ trên binary.
- Trong checker v2 marker chuẩn là 16 byte ASCII `D08 LAB MARKER\r\n`.
- Bản Linux `docs/TV1-VALIDATION.txt` chỉ là kết quả thử hash tại lúc tạo kit, không phải kiểm thử MSVC.
