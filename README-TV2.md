# TV2 — Phân tích tĩnh và detector

Điểm bắt đầu cho người tiếp nhận: [tv2/ban-giao/START-HERE.md](tv2/ban-giao/START-HERE.md). Tài liệu theo từng task: [tv2/README.md](tv2/README.md). Tình trạng chi tiết: [tv2/TASK-TRACKER.md](tv2/TASK-TRACKER.md).

Claude Code tự nạp `CLAUDE.md` khi mở dự án. Với công cụ khác, hãy chỉ định đọc `tv2/ban-giao/START-HERE.md` trước.

## Thành phần chính

| Nội dung | Đường dẫn |
|---|---|
| Báo cáo static | [tv2/G3-TV2-02/static-detector-report.md](tv2/G3-TV2-02/static-detector-report.md) |
| Cơ chế PE | [tv2/G1-TV2-01/pe-notes.md](tv2/G1-TV2-01/pe-notes.md) |
| Checklist dấu hiệu | [tv2/G1-TV2-01/static-checklist.md](tv2/G1-TV2-01/static-checklist.md) |
| Rule D0 | [tv2/G2-TV2-01/d0-rule.md](tv2/G2-TV2-01/d0-rule.md) |
| Đặc trưng | [tv2/G2-TV2-03/features.md](tv2/G2-TV2-03/features.md) |
| Bàn giao D1 (đề xuất) | [tv2/G2-TV2-03/D1-HANDOFF.md](tv2/G2-TV2-03/D1-HANDOFF.md) |
| Review TV1 | [tv2/G3-TV2-03/tv1-review.md](tv2/G3-TV2-03/tv1-review.md) |
| Việc cần người dùng | [tv2/HUONG-DAN-CHUP-ANH.md](tv2/HUONG-DAN-CHUP-ANH.md) |
| Mã detector | `detectors/tv2/` |
| Rule, manifest, lock | `configs/tv2/` |
| Schema | `schemas/tv2/` |
| Mẫu đối chứng đề xuất | `samples/tv2_controls/` |
| Minh chứng | `evidence/G1/TV2/`, `evidence/G2/TV2/`, `evidence/G3/TV2/`, `evidence/TV2-shared/` |

## Công cụ

Windows x64, Python 3.11, Visual Studio 2022 có C++ x64, MSYS2 MinGW-w64. Các công cụ sau nằm trong `artifacts/tools/` và không được đưa vào Git:

- Ghidra 12.2 từ bản phát hành chính thức.
- Temurin JDK 25, vì Ghidra 12.2 yêu cầu JDK 25 trở lên.
- Môi trường Python riêng có Capstone 6, jsonschema, PyGhidra.

Nếu máy khác chưa có `artifacts/tools/`, tải hai gói trên rồi tạo môi trường:

```powershell
python -m venv artifacts\tools\venv
artifacts\tools\venv\Scripts\python.exe -m pip install capstone==6.0.0 jsonschema pillow matplotlib
artifacts\tools\venv\Scripts\python.exe -m pip install --no-index --find-links artifacts\tools\ghidra_12.2_PUBLIC\Ghidra\Features\PyGhidra\pypkg\dist pyghidra
```

## Tái lập

Chạy từ thư mục gốc dự án:

```powershell
# 1. Build mới. Lệnh này tạo build_id mới và không thay binary cũ.
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\tv2-build.ps1

# 2. Phân tích headless bằng Ghidra cho build đang dùng trong báo cáo
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\tv2-ghidra.ps1 -BuildId 20261118-094956 -Samples 'B1,B2,P1'

# 3. Kiểm thử
artifacts\tools\venv\Scripts\python.exe tests\tv2\test_tv2.py

# 4. Chạy detector theo lock và đánh giá
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\tv2-evaluate-all.ps1 -Splits 'dev,test,probe'

# 5. Sinh lại bảng minh chứng và kiểm tra cuối
artifacts\tools\venv\Scripts\python.exe detectors\tv2\tv2report.py --docs-only
artifacts\tools\venv\Scripts\python.exe detectors\tv2\tv2linkcheck.py
```

Manifest đang trỏ tới build `20261118-094956`. Binary nằm trong `artifacts/` và không có trong Git. Nếu build lại, SHA-256 sẽ khác, nên phải tạo manifest và lock mới bằng `tv2manifest.py` và `tv2freeze.py`.

Chạy trên một binary:

```powershell
artifacts\tools\venv\Scripts\python.exe detectors\tv2\tv2detect.py extract <binary> -o features.json
artifacts\tools\venv\Scripts\python.exe detectors\tv2\tv2detect.py detect features.json --config configs\tv2\static-only.json
```

Không cần chạy mẫu để phân tích tĩnh. Các lệnh trên không thực thi binary.

## Giới hạn

- Build, nhãn, split và `TV2C-*` là sản phẩm hoặc đề xuất của TV2, chưa được nhóm duyệt.
- Ảnh GUI Ghidra và bảng D0/D1 chưa có.
- Kết quả hiện tại không phải đánh giá held-out chính thức.
