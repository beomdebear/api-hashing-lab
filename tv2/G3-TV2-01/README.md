# G3-TV2-01 — Đánh giá và phân tích FP/FN

Trạng thái: **Bị chặn ở phần cụ thể**.

## Tài liệu trong thư mục này

- Task này không có tài liệu riêng. Sản phẩm nằm ở phần dưới.

## Minh chứng và sản phẩm liên quan

- Thư mục minh chứng: [`evidence/G3/TV2/G3-TV2-01/`](../../evidence/G3/TV2/G3-TV2-01)
- [`evidence/G3/TV2/G3-TV2-01/error-analysis.md`](../../evidence/G3/TV2/G3-TV2-01/error-analysis.md)
- [`evidence/G3/TV2/G3-TV2-01/runs/`](../../evidence/G3/TV2/G3-TV2-01/runs)
- [`evidence/G3/TV2/G3-TV2-01/ghidra-headless/`](../../evidence/G3/TV2/G3-TV2-01/ghidra-headless)

## Còn thiếu

- Ảnh Ghidra của FP từ GUI.
- TV4 chưa duyệt nhãn, split và phần phân tích chung.

## Các bước

| Bước | Việc | Trạng thái | Còn thiếu |
|---|---|---|---|
| G3-TV2-01.01 | Chạy dev, test, probe theo lock | Hoàn thành và đã kiểm chứng | Không |
| G3-TV2-01.02 | Phân tích lỗi | Hoàn thành và đã kiểm chứng | Không |
| G3-TV2-01.03 | Chụp ảnh FP | Bị chặn ở phần cụ thể | Ảnh GUI Ghidra: cần người dùng chạy [`scripts/tv2-capture-gui.ps1`](../../scripts/tv2-capture-gui.ps1) (xem [`tv2/HUONG-DAN-CHUP-ANH.md`](../HUONG-DAN-CHUP-ANH.md)) |
| G3-TV2-01.04 | Đối chiếu cùng TV4 | Bị chặn ở phần cụ thể | Nhãn, split, dữ liệu TV4 |
