# Việc cần người dùng thực hiện

## 1. Chụp ảnh từ giao diện Ghidra

**Task còn thiếu:** ảnh của G1-TV2-02, G1-TV2-03, G2-TV2-01, G2-TV2-02, G3-TV2-01, và ảnh chú thích cho G3-TV2-02.

**Vì sao AI chưa tự làm được:** lệnh mở giao diện Ghidra bị chế độ kiểm soát quyền của Claude Code từ chối. Ngoài ra Ghidra hiển thị thỏa thuận người dùng ở lần mở GUI đầu tiên, và việc đồng ý nên do bạn quyết định.

**Đã thử:** chạy headless thành công cho 13 mẫu. Một lần khởi chạy GUI tự động bị từ chối trước khi Ghidra mở, nên AI không thử lại bằng đường khác.

**Đã chuẩn bị:** project Ghidra đã phân tích, script mở đúng từng binary, tự thêm chú thích `[TV2]`, chụp ảnh và ghi vào đúng thư mục.

> Script chụp ảnh **chưa được chạy thử với giao diện thật**. Mới kiểm tra cú pháp và phần ghép dải chú thích. Có thể cần sửa ở lần chạy đầu.

### Các bước, trên máy hiện tại (host), không cần VM

Script chỉ đọc project đã phân tích. Nó không chạy binary mẫu.

1. Mở PowerShell tại `D:\Study\HK5\Malware\api-hashing-lab`.
2. Thử trước với P1:

   ```powershell
   pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\tv2-capture-gui.ps1 -Only P1
   ```

3. Nếu Ghidra hiện **User Agreement**, hãy đọc và tự chọn. Nếu không đồng ý, script sẽ không tiếp tục.
4. Để yên cửa sổ Ghidra đến khi PowerShell in `finished: exit=0`. Không đóng hoặc thao tác trong cửa sổ.
5. Mở ảnh trong `evidence\G1\TV2\G1-TV2-03\images\`. Ảnh đúng có dải tiêu đề ghi `P1.exe`, SHA-256 bắt đầu bằng `0277D53B`, và thấy Listing cùng Decompiler.
6. Nếu ảnh đạt, chạy toàn bộ:

   ```powershell
   pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\tv2-capture-gui.ps1
   ```

### Kết quả mong đợi

| Thư mục | Tệp |
|---|---|
| `evidence/G1/TV2/G1-TV2-02/images/` | `B1-imports.png`, `B1-strings.png`, `B1-calls.png`, `B2-imports.png`, `B2-strings.png`, `B2-calls.png` |
| `evidence/G1/TV2/G1-TV2-03/images/` | `P1-1-hash-loop.png`, `P1-2-export-hash-compare.png`, `P1-3-resolve.png`, `P1-4-pointer-use.png` |
| `evidence/G2/TV2/G2-TV2-01/images/` | `P1-D0-C1-imports.png`, `P1-D0-C2-hash-loop.png`, `P1-D0-C3-indirect-call.png` |
| `evidence/G2/TV2/G2-TV2-02/images/` | `B3-name-table.png`, `B4-data-hash.png`, `B4-static-imports.png`, `B6-export-strcmp.png`, `B6-resolve.png` |
| `evidence/G3/TV2/G3-TV2-01/images/` | `B5-FP-D0-C1-imports.png`, `B5-FP-D0-C2-hash-loop.png`, `B5-FP-D0-resolve-by-name.png`, `B5-FP-D0-C3-indirect-call.png` |

Danh sách đã chụp nằm ở `artifacts/ghidra/20261118-094956/gui-capture-result.json`.

### Dấu hiệu lỗi

- PowerShell báo `Capture failed`, ảnh trống, hoặc chạy quá 40 phút.
- Khi đó hãy gửi lại toàn bộ chữ trong cửa sổ PowerShell.

### Nếu muốn chụp tay

Mở `artifacts\tools\ghidra_12.2_PUBLIC\ghidraRun.bat`, chọn JDK trong `artifacts\tools\jdk-25.0.5+8` nếu được hỏi, mở `artifacts\ghidra\20261118-094956\projects\TV2.gpr`, rồi đi tới các RVA trong `evidence/G1/TV2/G1-TV2-03/p1-evidence-chain.md`. Đặt ảnh đúng tên ở bảng trên.

### Gửi lại cho AI

Chỉ cần nói "đã chụp xong", kèm lỗi nếu có. AI sẽ kiểm tra ảnh, cập nhật báo cáo và chạy lại kiểm tra cuối.

## 2. Xác nhận từ nhóm

| Người | Cần xác nhận | Tài liệu gửi |
|---|---|---|
| TV1 | Danh sách dấu hiệu, các điểm review, binary và commit chốt | `tv2/G1-TV2-01/static-checklist.md`, `tv2/G3-TV2-03/tv1-review.md` |
| TV4 | TV2C-B3..B6, nhãn, split, bảng FP/FN | `evidence/G2/TV2/G2-TV2-02/control-signals.md`, `configs/tv2/manifest-provisional.csv`, `evidence/G3/TV2/G3-TV2-01/error-analysis.md` |
| Nhóm | Định nghĩa static-only, giao diện và kết quả D1, mốc tuần 7 | `tv2/G2-TV2-03/D1-HANDOFF.md` |

Gửi lại phản hồi hoặc đường dẫn kết quả. Nếu nhãn hay split thay đổi, AI sẽ tạo manifest và lượt chạy mới, không ghi đè kết quả cũ.
