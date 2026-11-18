# Theo dõi task TV2

Cập nhật: 2026-11-18T10:37:07+07:00. Trạng thái dùng đúng sáu mức trong prompt. Tệp được sinh từ `detectors/tv2/tv2tasks.py`.

| Task | Nội dung | Trạng thái | Còn thiếu |
|---|---|---|---|
| G1-TV2-01 | Cơ chế PE, imports, exports và địa chỉ hàm | Đã kiểm tra, còn thiếu minh chứng nghiệm thu | TV1 chưa xác nhận danh sách dấu hiệu chung. |
| G1-TV2-02 | Phân tích B1/B2 bằng Ghidra | Bị chặn ở phần cụ thể | Ảnh imports, strings và lời gọi từ GUI Ghidra. |
| G1-TV2-03 | Chuỗi bằng chứng API hashing trong P1 | Bị chặn ở phần cụ thể | Ảnh decompile có chú thích từ GUI Ghidra. |
| G2-TV2-01 | Baseline D0 | Bị chặn ở phần cụ thể | Ảnh minh họa match từ GUI Ghidra. |
| G2-TV2-02 | Đối chứng B3–B6 | Bị chặn ở phần cụ thể | Ảnh Ghidra từ GUI. TV4 chưa xác nhận TV2C-B3..B6 là B3–B6 chính thức. |
| G2-TV2-03 | Static features, bàn giao D1 và khóa rule | Bị chặn ở phần cụ thể | Commit khóa: bị chặn vì Git còn đường dẫn unmerged của TV3. Giao diện D1 thật và lịch mốc tuần 7 của nhóm chưa có. |
| G3-TV2-01 | Đánh giá và phân tích FP/FN | Bị chặn ở phần cụ thể | Ảnh Ghidra của FP từ GUI. TV4 chưa duyệt nhãn, split và phần phân tích chung. |
| G3-TV2-02 | Báo cáo static detector | Bị chặn ở phần cụ thể | Bảng D0/D1 thực đo: D1 chưa có. Ảnh chú thích từ GUI Ghidra. |
| G3-TV2-03 | Kiểm tra cuối và review PoC TV1 | Đã kiểm tra, còn thiếu minh chứng nghiệm thu | TV1 chưa phản hồi các điểm review. Cần chạy lại kiểm tra cuối sau khi có ảnh và commit khóa. |

## G1-TV2-01 — Cơ chế PE, imports, exports và địa chỉ hàm

### G1-TV2-01.01 — Vẽ sơ đồ cơ chế

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Mã máy B1/B2/P1 |
| Vị trí thao tác | `scripts/tv2-make-diagram.py` |
| Đầu ra | `docs/tv2/images/pe-mechanism.png` |
| Kiểm tra đã chạy | Đã mở ảnh kiểm tra bố cục và địa chỉ |
| Minh chứng | Ảnh sơ đồ |
| Còn thiếu | Không |
| Phụ thuộc | Không |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có sơ đồ PE và ba luồng |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-01.02 — Viết ghi chú PE

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | PE format, export Ghidra |
| Vị trí thao tác | `docs/tv2/pe-notes.md` |
| Đầu ra | Ghi chú |
| Kiểm tra đã chạy | Link checker |
| Minh chứng | `docs/tv2/pe-notes.md` |
| Còn thiếu | Không |
| Phụ thuộc | Không |
| Việc tiếp theo | Không |
| Tiêu chí xong | Giải thích được import sẵn khác resolve lúc chạy |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-01.03 — Lập static-checklist

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Kết quả phân tích |
| Vị trí thao tác | `docs/tv2/static-checklist.md` |
| Đầu ra | Checklist |
| Kiểm tra đã chạy | Link checker |
| Minh chứng | `docs/tv2/static-checklist.md` |
| Còn thiếu | Không |
| Phụ thuộc | Không |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có dấu hiệu, vị trí, cách kiểm và lỗi hiểu nhầm |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-01.04 — Thống nhất dấu hiệu với TV1

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | `docs/tv2/static-checklist.md` |
| Vị trí thao tác | Trao đổi nhóm |
| Đầu ra | Xác nhận của TV1 |
| Kiểm tra đã chạy | Chưa có |
| Minh chứng | Chưa có |
| Còn thiếu | Xác nhận của TV1 |
| Phụ thuộc | TV1 |
| Việc tiếp theo | Gửi checklist cho TV1 |
| Tiêu chí xong | Có ghi nhận TV1 đồng ý hoặc yêu cầu sửa |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G1-TV2-02 — Phân tích B1/B2 bằng Ghidra

### G1-TV2-02.01 — Build và định danh B1/B2

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Source TV1 |
| Vị trí thao tác | `scripts/tv2-build.ps1` |
| Đầu ra | `evidence/TV2-shared/build/20261118-094956/build-manifest.json` |
| Kiểm tra đã chạy | So SHA-256 trước khi nhập Ghidra |
| Minh chứng | Build manifest |
| Còn thiếu | Không |
| Phụ thuộc | MSVC |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có SHA-256 và provenance |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-02.02 — Phân tích headless

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | B1.exe, B2.exe |
| Vị trí thao tác | `scripts/tv2-ghidra.ps1` |
| Đầu ra | `ghidra-headless/` |
| Kiểm tra đã chạy | Đối chiếu với extractor |
| Minh chứng | `evidence/G2/TV2/G2-TV2-03/ghidra-crosscheck.csv` |
| Còn thiếu | Không |
| Phụ thuộc | Ghidra 12.2, JDK 25 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có imports, strings, calls, decompile |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-02.03 — Lập bảng B1/B2

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Export Ghidra |
| Vị trí thao tác | `detectors/tv2/tv2report.py` |
| Đầu ra | `b1-b2-comparison.md` |
| Kiểm tra đã chạy | Đọc lại bảng, kiểm tham chiếu chuỗi |
| Minh chứng | `b1-b2-comparison.md` |
| Còn thiếu | Không |
| Phụ thuộc | G1-TV2-02.02 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Chỉ ra B2 resolve theo tên, không hash |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-02.04 — Chụp ảnh GUI

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Project Ghidra |
| Vị trí thao tác | `scripts/tv2-capture-gui.ps1` |
| Đầu ra | `evidence/G1/TV2/G1-TV2-02/images/` |
| Kiểm tra đã chạy | Chưa chạy |
| Minh chứng | Chưa có |
| Còn thiếu | Ảnh GUI Ghidra: cần người dùng chạy `scripts/tv2-capture-gui.ps1` (xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`) |
| Phụ thuộc | Người dùng |
| Việc tiếp theo | Chạy script chụp ảnh |
| Tiêu chí xong | Có 6 ảnh B1/B2 từ Ghidra |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G1-TV2-03 — Chuỗi bằng chứng API hashing trong P1

### G1-TV2-03.01 — Truy chuỗi trên một binary P1

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | P1.exe |
| Vị trí thao tác | `detectors/tv2/tv2analysis.py` |
| Đầu ra | Features P1 |
| Kiểm tra đã chạy | Test chuỗi cùng binary |
| Minh chứng | `p1-evidence-chain.md` |
| Còn thiếu | Không |
| Phụ thuộc | G1-TV2-02.01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Đủ export → hash → so sánh → resolve → dùng con trỏ |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-03.02 — Đối chiếu bằng Ghidra

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Export Ghidra P1 |
| Vị trí thao tác | `detectors/tv2/tv2crosscheck.py` |
| Đầu ra | `ghidra-crosscheck.csv` |
| Kiểm tra đã chạy | RVA và mnemonic khớp |
| Minh chứng | `evidence/G2/TV2/G2-TV2-03/ghidra-crosscheck.csv` |
| Còn thiếu | Không |
| Phụ thuộc | G1-TV2-03.01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Mọi lệnh chuỗi có trong Ghidra |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G1-TV2-03.03 — Chụp ảnh decompile chú thích

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Project Ghidra |
| Vị trí thao tác | `scripts/tv2-capture-gui.ps1` |
| Đầu ra | `evidence/G1/TV2/G1-TV2-03/images/` |
| Kiểm tra đã chạy | Chưa chạy |
| Minh chứng | Bản văn bản headless |
| Còn thiếu | Ảnh GUI Ghidra: cần người dùng chạy `scripts/tv2-capture-gui.ps1` (xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`) |
| Phụ thuộc | Người dùng |
| Việc tiếp theo | Chạy script chụp ảnh |
| Tiêu chí xong | Có 4 ảnh P1 |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G2-TV2-01 — Baseline D0

### G2-TV2-01.01 — Viết extractor và rule D0

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Binary |
| Vị trí thao tác | `detectors/tv2/`, `configs/tv2/d0.json` |
| Đầu ra | CLI `tv2detect.py` |
| Kiểm tra đã chạy | `tests/tv2/test_tv2.py` |
| Minh chứng | Source, config |
| Còn thiếu | Không |
| Phụ thuộc | Capstone |
| Việc tiếp theo | Không |
| Tiêu chí xong | Chạy được trên binary thật |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-01.02 — Chạy tập phát triển

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Split dev |
| Vị trí thao tác | `scripts/tv2-evaluate-all.ps1` |
| Đầu ra | `runs/` |
| Kiểm tra đã chạy | Evaluator, schema |
| Minh chứng | `d0-dev-results.md` |
| Còn thiếu | Không |
| Phụ thuộc | Rule lock |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có kết luận và vị trí bằng chứng từng mẫu |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-01.03 — Chụp ảnh match

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Project Ghidra |
| Vị trí thao tác | `scripts/tv2-capture-gui.ps1` |
| Đầu ra | `evidence/G2/TV2/G2-TV2-01/images/` |
| Kiểm tra đã chạy | Chưa chạy |
| Minh chứng | Chưa có |
| Còn thiếu | Ảnh GUI Ghidra: cần người dùng chạy `scripts/tv2-capture-gui.ps1` (xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`) |
| Phụ thuộc | Người dùng |
| Việc tiếp theo | Chạy script chụp ảnh |
| Tiêu chí xong | Có 3 ảnh D0-C1, C2, C3 |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G2-TV2-02 — Đối chứng B3–B6

### G2-TV2-02.01 — Viết và build bốn mẫu đề xuất

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Điều kiện PDF |
| Vị trí thao tác | `samples/tv2_controls/` |
| Đầu ra | Binary TV2C-B3..B6 |
| Kiểm tra đã chạy | Build log, SHA-256 |
| Minh chứng | Build manifest |
| Còn thiếu | Không |
| Phụ thuộc | MSVC |
| Việc tiếp theo | Không |
| Tiêu chí xong | Đúng điều kiện B3/B6 và B4/B5 |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-02.02 — Phân tích bằng Ghidra và D0

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Binary đối chứng |
| Vị trí thao tác | `scripts/tv2-ghidra.ps1` |
| Đầu ra | `control-signals.md` |
| Kiểm tra đã chạy | Đối chiếu Ghidra, D0 |
| Minh chứng | `control-signals.md` |
| Còn thiếu | Không |
| Phụ thuộc | G2-TV2-01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có bảng dấu hiệu và FP/FN |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-02.03 — Chụp ảnh Ghidra

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Project Ghidra |
| Vị trí thao tác | `scripts/tv2-capture-gui.ps1` |
| Đầu ra | `evidence/G2/TV2/G2-TV2-02/images/` |
| Kiểm tra đã chạy | Chưa chạy |
| Minh chứng | Chưa có |
| Còn thiếu | Ảnh GUI Ghidra: cần người dùng chạy `scripts/tv2-capture-gui.ps1` (xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`) |
| Phụ thuộc | Người dùng |
| Việc tiếp theo | Chạy script chụp ảnh |
| Tiêu chí xong | Có ảnh B3, B4, B6 |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-02.04 — TV4 xác nhận mẫu

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Source và bảng dấu hiệu |
| Vị trí thao tác | Trao đổi nhóm |
| Đầu ra | Xác nhận TV4 |
| Kiểm tra đã chạy | Chưa có |
| Minh chứng | Chưa có |
| Còn thiếu | Xác nhận của TV4 |
| Phụ thuộc | TV4 |
| Việc tiếp theo | Gửi gói mẫu cho TV4 |
| Tiêu chí xong | TV4 chấp nhận hoặc yêu cầu sửa |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G2-TV2-03 — Static features, bàn giao D1 và khóa rule

### G2-TV2-03.01 — Trích đặc trưng và schema

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Binary |
| Vị trí thao tác | `detectors/tv2/tv2features.py` |
| Đầu ra | Features JSON |
| Kiểm tra đã chạy | Schema, test đổi tên, test ổn định |
| Minh chứng | `features-dev-summary.md` |
| Còn thiếu | Không |
| Phụ thuộc | G2-TV2-01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Mỗi đặc trưng có kiểu, trạng thái, bằng chứng |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-03.02 — Ví dụ thiếu bằng chứng

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | P1, B6, E1, B2 |
| Vị trí thao tác | `detectors/tv2/tv2report.py` |
| Đầu ra | `missing-evidence-examples.md` |
| Kiểm tra đã chạy | Schema |
| Minh chứng | `missing-evidence-examples.md` |
| Còn thiếu | Không |
| Phụ thuộc | G2-TV2-03.01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có ví dụ lỗi, không hỗ trợ, thiếu quan hệ |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-03.03 — Adapter đề xuất cho D1

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Features |
| Vị trí thao tác | `detectors/tv2/tv2d1adapter.py` |
| Đầu ra | `d1-input-dev/` |
| Kiểm tra đã chạy | Schema, test contract |
| Minh chứng | `d1-input-dev/` |
| Còn thiếu | D1 thật chưa có |
| Phụ thuộc | Nhóm |
| Việc tiếp theo | Thống nhất giao diện |
| Tiêu chí xong | Có bản ghi hợp lệ theo schema đề xuất |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-03.04 — Khóa rule bằng checksum

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Code, config, schema, manifest |
| Vị trí thao tác | `detectors/tv2/tv2freeze.py` |
| Đầu ra | `configs/tv2/locks/` |
| Kiểm tra đã chạy | `tv2freeze.py verify` |
| Minh chứng | Lock 1.0.0 và 1.0.1 |
| Còn thiếu | Không |
| Phụ thuộc | Không |
| Việc tiếp theo | Không |
| Tiêu chí xong | Lock kiểm tra được |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G2-TV2-03.05 — Commit khóa

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Lock 1.0.1 |
| Vị trí thao tác | Git |
| Đầu ra | Commit |
| Kiểm tra đã chạy | `git diff --diff-filter=U` còn 1 tệp |
| Minh chứng | Lock ghi rõ chưa có commit |
| Còn thiếu | Xử lý xung đột TV3, người dùng cho phép commit |
| Phụ thuộc | Người dùng, TV3 |
| Việc tiếp theo | Làm theo `docs/tv2/HUONG-DAN-CHUP-ANH.md` mục 2 |
| Tiêu chí xong | Có commit chứa đúng phiên bản lock |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G3-TV2-01 — Đánh giá và phân tích FP/FN

### G3-TV2-01.01 — Chạy dev, test, probe theo lock

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Lock 1.0.1 |
| Vị trí thao tác | `scripts/tv2-evaluate-all.ps1` |
| Đầu ra | `runs/` |
| Kiểm tra đã chạy | Lock verify, evaluator |
| Minh chứng | `runs/` |
| Còn thiếu | Không |
| Phụ thuộc | G2-TV2-03.04 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có prediction gốc từng mẫu |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G3-TV2-01.02 — Phân tích lỗi

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Prediction, Ghidra |
| Vị trí thao tác | `detectors/tv2/tv2report.py` |
| Đầu ra | `error-analysis.md` |
| Kiểm tra đã chạy | Kiểm chứng bằng symbol và Ghidra |
| Minh chứng | `error-analysis.md` |
| Còn thiếu | Không |
| Phụ thuộc | G3-TV2-01.01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có vị trí và lý do từng lỗi |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G3-TV2-01.03 — Chụp ảnh FP

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Project Ghidra |
| Vị trí thao tác | `scripts/tv2-capture-gui.ps1` |
| Đầu ra | `evidence/G3/TV2/G3-TV2-01/images/` |
| Kiểm tra đã chạy | Chưa chạy |
| Minh chứng | Chưa có |
| Còn thiếu | Ảnh GUI Ghidra: cần người dùng chạy `scripts/tv2-capture-gui.ps1` (xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`) |
| Phụ thuộc | Người dùng |
| Việc tiếp theo | Chạy script chụp ảnh |
| Tiêu chí xong | Có 4 ảnh FP của TV2C-B5 |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G3-TV2-01.04 — Đối chiếu cùng TV4

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | `error-analysis.md` |
| Vị trí thao tác | Trao đổi nhóm |
| Đầu ra | Xác nhận TV4 |
| Kiểm tra đã chạy | Chưa có |
| Minh chứng | Chưa có |
| Còn thiếu | Nhãn, split, dữ liệu TV4 |
| Phụ thuộc | TV4 |
| Việc tiếp theo | Gửi bảng lỗi cho TV4 |
| Tiêu chí xong | Có kết quả theo split chính thức |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G3-TV2-02 — Báo cáo static detector

### G3-TV2-02.01 — Viết báo cáo từ số liệu đo

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Run 1.0.1 |
| Vị trí thao tác | `detectors/tv2/tv2report.py` |
| Đầu ra | `docs/tv2/static-detector-report.md` |
| Kiểm tra đã chạy | Link checker, đối chiếu run |
| Minh chứng | Báo cáo |
| Còn thiếu | Không |
| Phụ thuộc | G3-TV2-01 |
| Việc tiếp theo | Không |
| Tiêu chí xong | Có cơ chế, rule, dữ liệu, kết quả, giới hạn |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G3-TV2-02.02 — Bảng D0/D1

| Mục | Nội dung |
|---|---|
| Trạng thái | Bị chặn ở phần cụ thể |
| Đầu vào | Kết quả D1 |
| Vị trí thao tác | Báo cáo mục 7 |
| Đầu ra | Bảng so sánh |
| Kiểm tra đã chạy | Chưa có |
| Minh chứng | Chỉ có D0 và static-only |
| Còn thiếu | Kết quả D1 thực đo |
| Phụ thuộc | Nhóm |
| Việc tiếp theo | Chạy lại generator khi có D1 |
| Tiêu chí xong | Có bảng D0/D1 cùng tập mẫu |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

## G3-TV2-03 — Kiểm tra cuối và review PoC TV1

### G3-TV2-03.01 — Review PoC trên binary

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Source, docs TV1, Ghidra |
| Vị trí thao tác | `docs/tv2/tv1-review.md` |
| Đầu ra | Checklist review |
| Kiểm tra đã chạy | Đối chiếu lệnh trong binary |
| Minh chứng | `docs/tv2/tv1-review.md` |
| Còn thiếu | TV1 chưa phản hồi |
| Phụ thuộc | TV1 |
| Việc tiếp theo | Gửi cho TV1 |
| Tiêu chí xong | Mỗi điểm có bằng chứng |
| Cập nhật | 2026-11-18T10:37:07+07:00 |

### G3-TV2-03.02 — Kiểm tra phiên bản và liên kết

| Mục | Nội dung |
|---|---|
| Trạng thái | Hoàn thành và đã kiểm chứng |
| Đầu vào | Tài liệu, lock, run |
| Vị trí thao tác | `detectors/tv2/tv2linkcheck.py` |
| Đầu ra | `final-check.md` |
| Kiểm tra đã chạy | Link checker |
| Minh chứng | `final-check.md` |
| Còn thiếu | Chạy lại sau khi thêm ảnh |
| Phụ thuộc | Các task trên |
| Việc tiếp theo | Chạy lại khi có thay đổi |
| Tiêu chí xong | Không thiếu file, cùng phiên bản |
| Cập nhật | 2026-11-18T10:37:07+07:00 |
