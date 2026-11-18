"""Single source for TV2 task status, used by the tracker and the evidence READMEs."""

DONE = "Hoàn thành và đã kiểm chứng"
CHECKED = "Đã kiểm tra, còn thiếu minh chứng nghiệm thu"
BLOCKED = "Bị chặn ở phần cụ thể"
GUI = "Ảnh GUI Ghidra: cần người dùng chạy `scripts/tv2-capture-gui.ps1` (xem `docs/tv2/HUONG-DAN-CHUP-ANH.md`)"


def step(sid, what, status, inputs, place, output, checks, evidence, missing, depends, next_action, done_when):
    return dict(id=sid, what=what, status=status, inputs=inputs, place=place, output=output, checks=checks,
                evidence=evidence, missing=missing, depends=depends, next=next_action, done_when=done_when)


TASKS = [
    {"id": "G1-TV2-01", "folder": "evidence/G1/TV2/G1-TV2-01", "title": "Cơ chế PE, imports, exports và địa chỉ hàm", "status": CHECKED,
     "have": ["`docs/tv2/images/pe-mechanism.png`", "`docs/tv2/pe-notes.md`", "`docs/tv2/static-checklist.md`"],
     "missing": ["TV1 chưa xác nhận danh sách dấu hiệu chung."],
     "steps": [
         step("G1-TV2-01.01", "Vẽ sơ đồ cơ chế", DONE, "Mã máy B1/B2/P1", "`scripts/tv2-make-diagram.py`", "`docs/tv2/images/pe-mechanism.png`", "Đã mở ảnh kiểm tra bố cục và địa chỉ", "Ảnh sơ đồ", "Không", "Không", "Không", "Có sơ đồ PE và ba luồng"),
         step("G1-TV2-01.02", "Viết ghi chú PE", DONE, "PE format, export Ghidra", "`docs/tv2/pe-notes.md`", "Ghi chú", "Link checker", "`docs/tv2/pe-notes.md`", "Không", "Không", "Không", "Giải thích được import sẵn khác resolve lúc chạy"),
         step("G1-TV2-01.03", "Lập static-checklist", DONE, "Kết quả phân tích", "`docs/tv2/static-checklist.md`", "Checklist", "Link checker", "`docs/tv2/static-checklist.md`", "Không", "Không", "Không", "Có dấu hiệu, vị trí, cách kiểm và lỗi hiểu nhầm"),
         step("G1-TV2-01.04", "Thống nhất dấu hiệu với TV1", BLOCKED, "`docs/tv2/static-checklist.md`", "Trao đổi nhóm", "Xác nhận của TV1", "Chưa có", "Chưa có", "Xác nhận của TV1", "TV1", "Gửi checklist cho TV1", "Có ghi nhận TV1 đồng ý hoặc yêu cầu sửa"),
     ]},
    {"id": "G1-TV2-02", "folder": "evidence/G1/TV2/G1-TV2-02", "title": "Phân tích B1/B2 bằng Ghidra", "status": BLOCKED,
     "have": ["`evidence/G1/TV2/G1-TV2-02/b1-b2-comparison.md`", "`evidence/G1/TV2/G1-TV2-02/ghidra-headless/`", "`scripts/tv2-ghidra.ps1`", "`scripts/ghidra/Tv2Export.java`"],
     "missing": ["Ảnh imports, strings và lời gọi từ GUI Ghidra."],
     "steps": [
         step("G1-TV2-02.01", "Build và định danh B1/B2", DONE, "Source TV1", "`scripts/tv2-build.ps1`", "`evidence/TV2-shared/build/20261118-094956/build-manifest.json`", "So SHA-256 trước khi nhập Ghidra", "Build manifest", "Không", "MSVC", "Không", "Có SHA-256 và provenance"),
         step("G1-TV2-02.02", "Phân tích headless", DONE, "B1.exe, B2.exe", "`scripts/tv2-ghidra.ps1`", "`ghidra-headless/`", "Đối chiếu với extractor", "`evidence/G2/TV2/G2-TV2-03/ghidra-crosscheck.csv`", "Không", "Ghidra 12.2, JDK 25", "Không", "Có imports, strings, calls, decompile"),
         step("G1-TV2-02.03", "Lập bảng B1/B2", DONE, "Export Ghidra", "`detectors/tv2/tv2report.py`", "`b1-b2-comparison.md`", "Đọc lại bảng, kiểm tham chiếu chuỗi", "`b1-b2-comparison.md`", "Không", "G1-TV2-02.02", "Không", "Chỉ ra B2 resolve theo tên, không hash"),
         step("G1-TV2-02.04", "Chụp ảnh GUI", BLOCKED, "Project Ghidra", "`scripts/tv2-capture-gui.ps1`", "`evidence/G1/TV2/G1-TV2-02/images/`", "Chưa chạy", "Chưa có", GUI, "Người dùng", "Chạy script chụp ảnh", "Có 6 ảnh B1/B2 từ Ghidra"),
     ]},
    {"id": "G1-TV2-03", "folder": "evidence/G1/TV2/G1-TV2-03", "title": "Chuỗi bằng chứng API hashing trong P1", "status": BLOCKED,
     "have": ["`evidence/G1/TV2/G1-TV2-03/p1-evidence-chain.md`", "`evidence/G1/TV2/G1-TV2-03/p1-decompile-annotated.md`", "`evidence/G1/TV2/G1-TV2-03/ghidra-headless/`"],
     "missing": ["Ảnh decompile có chú thích từ GUI Ghidra."],
     "steps": [
         step("G1-TV2-03.01", "Truy chuỗi trên một binary P1", DONE, "P1.exe", "`detectors/tv2/tv2analysis.py`", "Features P1", "Test chuỗi cùng binary", "`p1-evidence-chain.md`", "Không", "G1-TV2-02.01", "Không", "Đủ export → hash → so sánh → resolve → dùng con trỏ"),
         step("G1-TV2-03.02", "Đối chiếu bằng Ghidra", DONE, "Export Ghidra P1", "`detectors/tv2/tv2crosscheck.py`", "`ghidra-crosscheck.csv`", "RVA và mnemonic khớp", "`evidence/G2/TV2/G2-TV2-03/ghidra-crosscheck.csv`", "Không", "G1-TV2-03.01", "Không", "Mọi lệnh chuỗi có trong Ghidra"),
         step("G1-TV2-03.03", "Chụp ảnh decompile chú thích", BLOCKED, "Project Ghidra", "`scripts/tv2-capture-gui.ps1`", "`evidence/G1/TV2/G1-TV2-03/images/`", "Chưa chạy", "Bản văn bản headless", GUI, "Người dùng", "Chạy script chụp ảnh", "Có 4 ảnh P1"),
     ]},
    {"id": "G2-TV2-01", "folder": "evidence/G2/TV2/G2-TV2-01", "title": "Baseline D0", "status": BLOCKED,
     "have": ["`configs/tv2/d0.json`", "`docs/tv2/d0-rule.md`", "`evidence/G2/TV2/G2-TV2-01/d0-dev-results.md`", "`evidence/G2/TV2/G2-TV2-01/runs/`"],
     "missing": ["Ảnh minh họa match từ GUI Ghidra."],
     "steps": [
         step("G2-TV2-01.01", "Viết extractor và rule D0", DONE, "Binary", "`detectors/tv2/`, `configs/tv2/d0.json`", "CLI `tv2detect.py`", "`tests/tv2/test_tv2.py`", "Source, config", "Không", "Capstone", "Không", "Chạy được trên binary thật"),
         step("G2-TV2-01.02", "Chạy tập phát triển", DONE, "Split dev", "`scripts/tv2-evaluate-all.ps1`", "`runs/`", "Evaluator, schema", "`d0-dev-results.md`", "Không", "Rule lock", "Không", "Có kết luận và vị trí bằng chứng từng mẫu"),
         step("G2-TV2-01.03", "Chụp ảnh match", BLOCKED, "Project Ghidra", "`scripts/tv2-capture-gui.ps1`", "`evidence/G2/TV2/G2-TV2-01/images/`", "Chưa chạy", "Chưa có", GUI, "Người dùng", "Chạy script chụp ảnh", "Có 3 ảnh D0-C1, C2, C3"),
     ]},
    {"id": "G2-TV2-02", "folder": "evidence/G2/TV2/G2-TV2-02", "title": "Đối chứng B3–B6", "status": BLOCKED,
     "have": ["`samples/tv2_controls/`", "`evidence/G2/TV2/G2-TV2-02/control-signals.md`", "`evidence/G2/TV2/G2-TV2-02/ghidra-headless/`"],
     "missing": ["Ảnh Ghidra từ GUI.", "TV4 chưa xác nhận TV2C-B3..B6 là B3–B6 chính thức."],
     "steps": [
         step("G2-TV2-02.01", "Viết và build bốn mẫu đề xuất", DONE, "Điều kiện PDF", "`samples/tv2_controls/`", "Binary TV2C-B3..B6", "Build log, SHA-256", "Build manifest", "Không", "MSVC", "Không", "Đúng điều kiện B3/B6 và B4/B5"),
         step("G2-TV2-02.02", "Phân tích bằng Ghidra và D0", DONE, "Binary đối chứng", "`scripts/tv2-ghidra.ps1`", "`control-signals.md`", "Đối chiếu Ghidra, D0", "`control-signals.md`", "Không", "G2-TV2-01", "Không", "Có bảng dấu hiệu và FP/FN"),
         step("G2-TV2-02.03", "Chụp ảnh Ghidra", BLOCKED, "Project Ghidra", "`scripts/tv2-capture-gui.ps1`", "`evidence/G2/TV2/G2-TV2-02/images/`", "Chưa chạy", "Chưa có", GUI, "Người dùng", "Chạy script chụp ảnh", "Có ảnh B3, B4, B6"),
         step("G2-TV2-02.04", "TV4 xác nhận mẫu", BLOCKED, "Source và bảng dấu hiệu", "Trao đổi nhóm", "Xác nhận TV4", "Chưa có", "Chưa có", "Xác nhận của TV4", "TV4", "Gửi gói mẫu cho TV4", "TV4 chấp nhận hoặc yêu cầu sửa"),
     ]},
    {"id": "G2-TV2-03", "folder": "evidence/G2/TV2/G2-TV2-03", "title": "Static features, bàn giao D1 và khóa rule", "status": BLOCKED,
     "have": ["`detectors/tv2/tv2features.py`", "`schemas/tv2/static-features-1.0.schema.json`", "`docs/tv2/features.md`", "`docs/tv2/rule-changelog.md`", "`docs/tv2/D1-HANDOFF.md`", "`configs/tv2/locks/rule-lock-1.0.1.json`", "`evidence/G2/TV2/G2-TV2-03/features-dev-summary.md`", "`evidence/G2/TV2/G2-TV2-03/missing-evidence-examples.md`"],
     "missing": ["Commit khóa: bị chặn vì Git còn đường dẫn unmerged của TV3.", "Giao diện D1 thật và lịch mốc tuần 7 của nhóm chưa có."],
     "steps": [
         step("G2-TV2-03.01", "Trích đặc trưng và schema", DONE, "Binary", "`detectors/tv2/tv2features.py`", "Features JSON", "Schema, test đổi tên, test ổn định", "`features-dev-summary.md`", "Không", "G2-TV2-01", "Không", "Mỗi đặc trưng có kiểu, trạng thái, bằng chứng"),
         step("G2-TV2-03.02", "Ví dụ thiếu bằng chứng", DONE, "P1, B6, E1, B2", "`detectors/tv2/tv2report.py`", "`missing-evidence-examples.md`", "Schema", "`missing-evidence-examples.md`", "Không", "G2-TV2-03.01", "Không", "Có ví dụ lỗi, không hỗ trợ, thiếu quan hệ"),
         step("G2-TV2-03.03", "Adapter đề xuất cho D1", DONE, "Features", "`detectors/tv2/tv2d1adapter.py`", "`d1-input-dev/`", "Schema, test contract", "`d1-input-dev/`", "D1 thật chưa có", "Nhóm", "Thống nhất giao diện", "Có bản ghi hợp lệ theo schema đề xuất"),
         step("G2-TV2-03.04", "Khóa rule bằng checksum", DONE, "Code, config, schema, manifest", "`detectors/tv2/tv2freeze.py`", "`configs/tv2/locks/`", "`tv2freeze.py verify`", "Lock 1.0.0 và 1.0.1", "Không", "Không", "Không", "Lock kiểm tra được"),
         step("G2-TV2-03.05", "Commit khóa", BLOCKED, "Lock 1.0.1", "Git", "Commit", "`git diff --diff-filter=U` còn 1 tệp", "Lock ghi rõ chưa có commit", "Xử lý xung đột TV3, người dùng cho phép commit", "Người dùng, TV3", "Làm theo `docs/tv2/HUONG-DAN-CHUP-ANH.md` mục 2", "Có commit chứa đúng phiên bản lock"),
     ]},
    {"id": "G3-TV2-01", "folder": "evidence/G3/TV2/G3-TV2-01", "title": "Đánh giá và phân tích FP/FN", "status": BLOCKED,
     "have": ["`evidence/G3/TV2/G3-TV2-01/error-analysis.md`", "`evidence/G3/TV2/G3-TV2-01/runs/`", "`evidence/G3/TV2/G3-TV2-01/ghidra-headless/`"],
     "missing": ["Ảnh Ghidra của FP từ GUI.", "TV4 chưa duyệt nhãn, split và phần phân tích chung."],
     "steps": [
         step("G3-TV2-01.01", "Chạy dev, test, probe theo lock", DONE, "Lock 1.0.1", "`scripts/tv2-evaluate-all.ps1`", "`runs/`", "Lock verify, evaluator", "`runs/`", "Không", "G2-TV2-03.04", "Không", "Có prediction gốc từng mẫu"),
         step("G3-TV2-01.02", "Phân tích lỗi", DONE, "Prediction, Ghidra", "`detectors/tv2/tv2report.py`", "`error-analysis.md`", "Kiểm chứng bằng symbol và Ghidra", "`error-analysis.md`", "Không", "G3-TV2-01.01", "Không", "Có vị trí và lý do từng lỗi"),
         step("G3-TV2-01.03", "Chụp ảnh FP", BLOCKED, "Project Ghidra", "`scripts/tv2-capture-gui.ps1`", "`evidence/G3/TV2/G3-TV2-01/images/`", "Chưa chạy", "Chưa có", GUI, "Người dùng", "Chạy script chụp ảnh", "Có 4 ảnh FP của TV2C-B5"),
         step("G3-TV2-01.04", "Đối chiếu cùng TV4", BLOCKED, "`error-analysis.md`", "Trao đổi nhóm", "Xác nhận TV4", "Chưa có", "Chưa có", "Nhãn, split, dữ liệu TV4", "TV4", "Gửi bảng lỗi cho TV4", "Có kết quả theo split chính thức"),
     ]},
    {"id": "G3-TV2-02", "folder": "evidence/G3/TV2/G3-TV2-02", "title": "Báo cáo static detector", "status": BLOCKED,
     "have": ["`docs/tv2/static-detector-report.md`"],
     "missing": ["Bảng D0/D1 thực đo: D1 chưa có.", "Ảnh chú thích từ GUI Ghidra."],
     "steps": [
         step("G3-TV2-02.01", "Viết báo cáo từ số liệu đo", DONE, "Run 1.0.1", "`detectors/tv2/tv2report.py`", "`docs/tv2/static-detector-report.md`", "Link checker, đối chiếu run", "Báo cáo", "Không", "G3-TV2-01", "Không", "Có cơ chế, rule, dữ liệu, kết quả, giới hạn"),
         step("G3-TV2-02.02", "Bảng D0/D1", BLOCKED, "Kết quả D1", "Báo cáo mục 7", "Bảng so sánh", "Chưa có", "Chỉ có D0 và static-only", "Kết quả D1 thực đo", "Nhóm", "Chạy lại generator khi có D1", "Có bảng D0/D1 cùng tập mẫu"),
     ]},
    {"id": "G3-TV2-03", "folder": "evidence/G3/TV2/G3-TV2-03", "title": "Kiểm tra cuối và review PoC TV1", "status": CHECKED,
     "have": ["`docs/tv2/tv1-review.md`", "`evidence/G3/TV2/G3-TV2-03/final-check.md`", "`docs/tv2/rule-changelog.md`"],
     "missing": ["TV1 chưa phản hồi các điểm review.", "Cần chạy lại kiểm tra cuối sau khi có ảnh và commit khóa."],
     "steps": [
         step("G3-TV2-03.01", "Review PoC trên binary", DONE, "Source, docs TV1, Ghidra", "`docs/tv2/tv1-review.md`", "Checklist review", "Đối chiếu lệnh trong binary", "`docs/tv2/tv1-review.md`", "TV1 chưa phản hồi", "TV1", "Gửi cho TV1", "Mỗi điểm có bằng chứng"),
         step("G3-TV2-03.02", "Kiểm tra phiên bản và liên kết", DONE, "Tài liệu, lock, run", "`detectors/tv2/tv2linkcheck.py`", "`final-check.md`", "Link checker", "`final-check.md`", "Chạy lại sau khi thêm ảnh", "Các task trên", "Chạy lại khi có thay đổi", "Không thiếu file, cùng phiên bản"),
     ]},
]
