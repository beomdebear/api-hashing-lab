# Đặc tả thực thi TV2

Tệp này lưu yêu cầu lâu dài. Tiến độ nằm trong [TASK-TRACKER.md](TASK-TRACKER.md). Prompt gốc: [PROMPT-CLAUDE-TV2.md](../prompt-claude/PROMPT-CLAUDE-TV2.md).

## 1. Tài liệu nguồn

| Tài liệu | Đường dẫn | SHA-256 | Vai trò |
|---|---|---|---|
| PDF phân công | `prompt-claude/API-Hashing.pdf` (2 trang) | `74BD097829794E04E63C51FB51B9F08D35B7B2203D203F16AB0B372B77453999` | Yêu cầu bài tập, là PDF duy nhất trong thư mục |
| Prompt của người dùng | `prompt-claude/PROMPT-CLAUDE-TV2.md` | `7E54DB6F4B535ECC94BA01CAED832723EAED32F83D5AE4BC104314CB8B9C8662` | Chỉ thị thực hiện |

Khi bắt đầu phiên mới, tính lại SHA-256 của PDF. Nếu khác giá trị trên, đọc lại toàn bộ PDF và cập nhật bảng dưới.

## 2. Yêu cầu trong PDF

| Task | Trang | Việc cần làm | Hoàn thành khi | Minh chứng PDF yêu cầu |
|---|---:|---|---|---|
| G1-TV2-01 | 1 | Vẽ quan hệ PE, imports, exports và địa chỉ hàm; thống nhất dấu hiệu cần quan sát với TV1 | Giải thích được khác biệt giữa import sẵn và tìm hàm lúc chạy | Sơ đồ cơ chế; ghi chú PE; danh sách dấu hiệu trong `static-checklist.md` |
| G1-TV2-02 | 1 | Mở B1/B2 bằng Ghidra; so imports, strings và vị trí gọi API | Chỉ ra vì sao B2 là resolve động nhưng chưa phải API hashing | Ảnh imports, strings và lời gọi; project Ghidra hoặc script nhập lại; bảng so sánh B1/B2 |
| G1-TV2-03 | 1 | Phân tích P1 từ tên export đến vòng hash, phép so sánh và lời gọi gián tiếp | Đánh dấu được chuỗi bằng chứng trong cùng binary P1 | Ảnh decompile có chú thích; SHA-256 binary; ghi chú hàm và địa chỉ theo module + RVA |
| G2-TV2-01 | 1 | Xây D0 bằng dấu hiệu đơn giản trên tập phát triển; mô tả chính xác rule | D0 xuất kết luận và vị trí bằng chứng; không đọc nhãn hoặc log tự khai của PoC | Source hoặc rule D0; cấu hình; kết quả từng mẫu phát triển; ảnh minh họa match |
| G2-TV2-02 | 1 | Cùng TV4 tạo và phân tích B3–B6 để kiểm tra báo động nhầm | B3/B6 resolve tên hợp lệ; B4/B5 hash dữ liệu nhưng không dùng hash để tìm API | Source mẫu đối chứng; ảnh Ghidra; bảng dấu hiệu và FP/FN ban đầu của D0 |
| G2-TV2-03 | 1 | Trích đặc trưng theo quan hệ export → hash → so sánh → resolve; bàn giao static features cho D1 và khóa rule | Giải thích được mỗi đặc trưng; có ví dụ thiếu bằng chứng; chốt rule cuối tuần 7 | Script trích xuất; schema features; features tập phát triển; ghi chú chỉnh rule và commit khóa |
| G3-TV2-01 | 2 | Chạy static-only và D0 theo cấu hình đã khóa; phân tích từng FP/FN cùng TV4 | Kết quả từng mẫu có vị trí bằng chứng và lý do đúng/sai | Prediction gốc; ảnh Ghidra của FP/FN; bảng phân tích lỗi; thời gian phân tích |
| G3-TV2-02 | 2 | Viết phần static detector; chọn ví dụ D0/D1 theo kết quả thực đo | Không dàn dựng D0 phải bỏ sót; nêu giới hạn thuật toán và compiler nếu đã quan sát | Bản thảo static; ảnh chú thích; bảng D0/D1; ví dụ demo có run_id |
| G3-TV2-03 | 2 | Kiểm tra rule cuối và liên kết minh chứng trong báo cáo; review phần PoC của TV1 | Rule, bảng kết quả và báo cáo cùng phiên bản; liên kết không thiếu file | Bản rule chốt; checklist review; danh sách lỗi đã sửa; báo cáo phần static hoàn chỉnh |

## 3. Yêu cầu của người dùng còn hiệu lực

- AI trực tiếp làm tối đa, chỉ bàn giao việc thật sự cần người dùng, kèm lý do và hướng dẫn cụ thể.
- Bảo toàn Git: không reset/clean/stash, không sửa phần việc của thành viên khác, không commit ngoài phạm vi, không push khi chưa được yêu cầu.
- Không tự ghi TV1/TV3/TV4 đã xác nhận. Mẫu và split do TV2 tạo chỉ là đề xuất.
- Không dùng nhãn, tên mẫu, source, bảng hash, audit hay log tự khai làm đặc trưng dự đoán.
- Thay thế kỹ thuật không thay thế tiêu chí nghiệm thu: build mới không phải binary lịch sử, output headless không phải ảnh GUI.
- Lưu báo cáo `tv2/ban-giao/DD-MM-YYYY_HH-mm.md` theo UTC+7, cập nhật `tv2/ban-giao/START-HERE.md` sau cùng.
- Điều chỉnh ngày 2026-11-18: tài liệu TV2 đặt ở `tv2/`, ngang hàng với `docs/`, mỗi task một thư mục. Chỉ thị này thay cấu trúc `docs/tv2/` được gợi ý trong prompt. Báo cáo bàn giao đặt ở `tv2/ban-giao/`, thay vị trí `ban-giao/` ở gốc trong prompt. Minh chứng vẫn ở `evidence/G*/TV2/`.

## 4. Lựa chọn triển khai của TV2 (chưa được nhóm duyệt)

| Mục | Quyết định | Căn cứ |
|---|---|---|
| Dataset build | Build mới `20261118-094956` trên máy phát triển | Không truy cập được binary lịch sử (`C:\Users\quyng\...`); build mới không mang SHA lịch sử |
| Công cụ | Ghidra 12.2 + Temurin JDK 25 bản portable trong `artifacts/tools/` | Ghidra 12.2 yêu cầu JDK 25+; máy chỉ có JDK 24 |
| Mẫu đối chứng | `TV2C-B3..B6` trong `samples/tv2_controls/` | PDF yêu cầu vai trò B3–B6; TV4 chưa xác nhận |
| Định nghĩa D0 | `configs/tv2/d0.json`: GetProcAddress + vòng giống hash + lời gọi gián tiếp ngoài IAT | Dấu hiệu đơn giản, chọn trên B1/B2/P1 |
| Định nghĩa static-only | `configs/tv2/static-only.json`: chuỗi quan hệ đã xác minh | Giả định của TV2; nhóm chưa định nghĩa static-only |
| Nhãn và split | `configs/tv2/*-provisional.csv` | TV4 giữ nhãn và split chính thức |
| Khóa rule | `configs/tv2/locks/` bằng checksum; commit `1befa67` chứa đúng các tệp của lock 1.0.1 | Commit do người dùng tạo, đã đối chiếu từng checksum trong `configs/tv2/locks/lock-commits.json` |
| Ảnh GUI | Người dùng chạy `scripts/tv2-capture-gui.ps1` | Lệnh tự mở GUI bị kiểm soát quyền từ chối; thỏa thuận người dùng của Ghidra do người dùng tự quyết định |

## 5. Quy tắc đánh giá

- `dev`: B1, B2, P1, TV2C-B3, TV2C-B4. `test`: P2–P5, E1, E2, TV2C-B5, TV2C-B6. `probe`: biến thể compiler, không gộp vào metric chính.
- Rule được khóa trước khi chạy `test`. Sau khi xem test, mọi thay đổi thành phiên bản mới; giữ kết quả cũ.
- Lỗi phân tích cho `unknown`, không bao giờ thành `negative`.
- Các mẫu cùng họ PoC không được coi là họ độc lập; số liệu chỉ là thử nghiệm nội bộ.

## 6. Ràng buộc kỹ thuật cần giữ

- GetProcAddress nhận tên hoặc ordinal, không nhận hash của PoC. Resolver của P1 tìm tên bằng hash rồi truyền tên đó.
- PoC không duyệt PEB và không tự tính địa chỉ qua AddressOfFunctions.
- Phân biệt file offset, RVA, VA tĩnh, VA runtime. Forwarded export có thể trả địa chỉ trong KernelBase.
- Không trộn địa chỉ của nhiều build.
