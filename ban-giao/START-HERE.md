# START HERE — TV2 API Hashing Lab

- Cập nhật: 2026-11-18T10:37:08+07:00
- Dự án: API Hashing Lab. Phạm vi: 9 task TV2 (G1, G2, G3).
- Prompt: `prompt-claude/PROMPT-CLAUDE-TV2.md`. PDF: `prompt-claude/API-Hashing.pdf`.
- Đặc tả: `docs/tv2/EXECUTION-SPEC.md`. Tracker: `docs/tv2/TASK-TRACKER.md`.
- Nhánh `TV2`, HEAD `7ee5880387d326e276f306c42b20cfe03dbb9bf8`, có thay đổi chưa commit.
- Báo cáo hợp lệ mới nhất: [18-11-2026_10-37.md](18-11-2026_10-37.md) (kết thúc phiên).

## Thứ tự đọc

1. `CLAUDE.md`
2. `docs/tv2/EXECUTION-SPEC.md`, rồi tính lại SHA-256 của PDF để so
3. Báo cáo mới nhất ở trên
4. `docs/tv2/TASK-TRACKER.md`
5. `git status` và `artifacts/tools/venv/Scripts/python.exe detectors/tv2/tv2freeze.py verify configs/tv2/locks/rule-lock-1.0.1.json`

## Tình trạng

- **Đã có và đã kiểm tra:** sơ đồ và ghi chú PE, phân tích Ghidra headless 13 mẫu, chuỗi bằng chứng P1, D0, static-only, features, lock 1.0.1, kết quả dev/test/probe, phân tích lỗi, review TV1.
- **Chưa task nào đạt đủ nghiệm thu.** G1-TV2-01 và G3-TV2-03 còn chờ phản hồi của TV1. Bảy task còn lại bị chặn ở ảnh GUI, commit khóa, D1 hoặc xác nhận của TV4.
- **Trở ngại:** lệnh tự mở GUI Ghidra bị từ chối; Git còn xung đột của TV3; chưa có D1.

## Bước tiếp tục chính xác

- Task: G1-TV2-02.04, G1-TV2-03.03, G2-TV2-01.03, G2-TV2-02.03, G3-TV2-01.03.
- Đầu vào: ảnh do người dùng tạo bằng `scripts/tv2-capture-gui.ps1`.
- Hành động: kiểm tra ảnh theo bảng trong `docs/tv2/HUONG-DAN-CHUP-ANH.md`, cập nhật `detectors/tv2/tv2tasks.py`, chạy `detectors/tv2/tv2report.py` và `detectors/tv2/tv2linkcheck.py`.
- Xong khi: `evidence/G3/TV2/G3-TV2-03/final-check.md` báo thiếu 0 ảnh và 0 lỗi.

## Việc cần người dùng

Xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`: chụp ảnh GUI, mở khóa commit, lấy xác nhận từ TV1, TV4 và nhóm.

## Lưu ý Git và tệp cần bảo toàn

- Không xử lý `evidence/G1/TV3/G1-TV3-01/environment.md`. Không reset, clean, stash hoặc đổi nhánh. Không commit khi chưa được yêu cầu.
- Không chạy `scripts/tv1-generate-hashes.py`.
- Không sửa tệp thuộc lock 1.0.1 nếu không tạo phiên bản mới. Giữ nguyên các thư mục `runs/`.
- `artifacts/` không vào Git nhưng đang chứa binary, project Ghidra và công cụ. Đừng xóa nếu chưa có bản thay thế.
