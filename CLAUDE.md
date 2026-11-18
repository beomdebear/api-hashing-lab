# Chỉ dẫn dự án cho phần TV2

Bạn đang hỗ trợ **TV2 (phân tích tĩnh)** của API Hashing Lab, gồm 9 task: G1-TV2-01..03, G2-TV2-01..03, G3-TV2-01..03.

**Khi bắt đầu phiên mới hoặc khôi phục context, đọc `ban-giao/START-HERE.md`, làm quy trình khôi phục rồi tiếp tục theo yêu cầu hiện tại của người dùng.**

- Prompt gốc: `prompt-claude/PROMPT-CLAUDE-TV2.md`
- PDF phân công: `prompt-claude/API-Hashing.pdf`
- Đặc tả lâu dài: `docs/tv2/EXECUTION-SPEC.md`
- Trạng thái chi tiết: `docs/tv2/TASK-TRACKER.md`

## Quy tắc áp dụng mọi phiên

- Không reset, clean, stash, đổi nhánh để né trạng thái hiện tại. Không xử lý xung đột của TV3 trong `evidence/G1/TV3/G1-TV3-01/environment.md`.
- Không commit hoặc push nếu người dùng chưa yêu cầu. Không chạy `scripts/tv1-generate-hashes.py`, vì nó ghi đè `main.c` của TV1.
- Detector chỉ nhận dữ liệu quan sát từ binary. Không cho nó đọc nhãn, tên mẫu, source, bảng hash hay log của PoC.
- Sau khi đã xem kết quả test, mọi thay đổi detector phải thành phiên bản và lock mới; giữ nguyên kết quả cũ.
- Báo cáo đúng thực tế: không gọi output headless là ảnh GUI, không ghi TV1/TV3/TV4 đã xác nhận khi chưa có bằng chứng.
- Sau mốc quan trọng, cập nhật `docs/tv2/TASK-TRACKER.md`, thêm báo cáo `ban-giao/DD-MM-YYYY_HH-mm.md` (UTC+7), rồi cập nhật `ban-giao/START-HERE.md` sau cùng.
