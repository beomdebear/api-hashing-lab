# Báo cáo phần static detector

Trạng thái: **bản thảo**. Thiếu ảnh GUI Ghidra và số liệu D1. Nhãn, split và các mẫu `TV2C-*` là đề xuất của TV2, chưa được nhóm duyệt.

## 1. Mục tiêu

Phát hiện tĩnh việc một chương trình PE32+ x64 tìm API bằng hash của tên export. Detector chỉ đọc byte của binary và không chạy mẫu.

## 2. Cơ chế cần phát hiện

Import sẵn để loader điền IAT. Resolve động theo tên gọi `GetProcAddress` với tên có trong chương trình. API hashing không cần giữ tên đích: chương trình duyệt tên export, hash từng tên, so với giá trị đích rồi dùng tên khớp. Xem [ghi chú PE](pe-notes.md) và [sơ đồ](images/pe-mechanism.png).

## 3. Phương pháp

1. Đọc PE32+, import, `.pdata` và giải mã lệnh bằng Capstone.
2. Dựng CFG và lan truyền nhãn dữ liệu trong từng hàm, kèm tóm tắt hàm để đi qua lời gọi và tham số out.
3. Dùng phụ thuộc điều khiển để biết tên export chỉ được giữ khi phép so hash đúng.
4. Ghi đặc trưng và vị trí bằng chứng vào tài liệu có schema.
5. Áp rule từ cấu hình có phiên bản. Phân tích lỗi cho `unknown`, không cho `negative`.

## 4. Rule

- **D0** ([chi tiết](d0-rule.md)): import `GetProcAddress`, có vòng giống hash, có lời gọi gián tiếp ngoài IAT. Rule chỉ xét đồng xuất hiện.
- **Static-only** (định nghĩa làm việc của TV2): cả năm quan hệ duyệt tên export, tên → hash, hash → so sánh, so sánh → chọn tên, tên → resolve phải được xác minh. Việc dùng con trỏ được báo cáo nhưng không bắt buộc, vì E1 resolve mà không gọi địa chỉ.
- Danh sách đặc trưng ở [features.md](features.md). Lịch sử thay đổi ở [rule-changelog.md](rule-changelog.md).

## 5. Dữ liệu và quy trình

- Build `20261118-094956`, MSVC `/Od /MD`, cây nguồn có thay đổi chưa commit. Provenance ở `evidence/TV2-shared/build/20261118-094956/build-manifest.json`.
- Tập phát triển: B1, B2, P1, TV2C-B3, TV2C-B4. Tập test: P2–P5, E1, E2, TV2C-B5, TV2C-B6. Năm mẫu probe chỉ dùng để quan sát compiler.
- Rule được khóa trước khi chạy test. Lock hiện tại `1.0.1`, tạo lúc `2026-11-18T10:13:26+07:00`, gồm checksum code, config, schema và manifest.
- Commit khóa **chưa có**: the index has unmerged paths.

## 6. Kết quả thực đo

Run: dev `R-20261118T031326Z-dev-1.0.1`, test `R-20261118T031327Z-test-1.0.1`, probe `R-20261118T031328Z-probe-1.0.1`. Lock 1.0.0 và 1.0.1 cho cùng kết luận trên tập test.

| Tập | Detector | Số mẫu | Phân tích ok | TP | TN | FP | FN | Unknown | Precision | Recall | F1 | Trung vị ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev | d0 | 5 | 5 | 1 | 4 | 0 | 0 | 0 | 1.0 | 1.0 | 1.0 | 33.6 |
| dev | static-only | 5 | 5 | 1 | 4 | 0 | 0 | 0 | 1.0 | 1.0 | 1.0 | 33.6 |
| test | d0 | 8 | 8 | 6 | 1 | 1 | 0 | 0 | 0.8571 | 1.0 | 0.9231 | 123.7 |
| test | static-only | 8 | 8 | 6 | 2 | 0 | 0 | 0 | 1.0 | 1.0 | 1.0 | 123.7 |

### Từng mẫu của tập test

| Mẫu | SHA-256 | Nhãn đề xuất | D0 | Static-only |
|---|---|---|---|---|
| E1 | 2916E4F9E886E863… | positive | positive (TP) | positive (TP) |
| E2 | F24E0C6E2066452C… | positive | positive (TP) | positive (TP) |
| P2 | C0A9BE62C1B2B7EF… | positive | positive (TP) | positive (TP) |
| P3 | 9D9F49C84A60E629… | positive | positive (TP) | positive (TP) |
| P4 | 9750799FF7B91A59… | positive | positive (TP) | positive (TP) |
| P5 | 0ABF1577D295D3B1… | positive | positive (TP) | positive (TP) |
| TV2C-B5 | EB8A4426E124E966… | negative | positive (FP) | negative (TN) |
| TV2C-B6 | 6E7DCBA2D1CAAA8E… | negative | negative (TN) | negative (TN) |

Lý do và vị trí bằng chứng từng mẫu nằm trong `evidence/G3/TV2/G3-TV2-01/runs/R-20261118T031327Z-test-1.0.1/per-sample.csv`. Phân tích lỗi ở `evidence/G3/TV2/G3-TV2-01/error-analysis.md`.

## 7. Bảng D0/D1

**Chưa lập được.** Repository chưa có D1 hay kết quả D1, nên không có số liệu để so. Bảng trên so D0 với static-only và không thay thế bảng D0/D1. Đầu vào đề xuất cho D1 ở [D1-HANDOFF.md](D1-HANDOFF.md).

## 8. Ví dụ demo theo kết quả thực đo

| Ví dụ | Binary | Run | Điều quan sát |
|---|---|---|---|
| Chuỗi đầy đủ | P1, `0277D53B1124978B29154BFA4C11CA62E69CCCF4AF614199DA8D2A5401366787` | `R-20261118T031326Z-dev-1.0.1` | Cả D0 và static-only báo dương; chuỗi RVA ở `evidence/G1/TV2/G1-TV2-03/p1-evidence-chain.md` |
| Báo động nhầm của D0 | TV2C-B5, `EB8A4426E124E9660B8E7B73F8B6D52AE596AC015F14809D85AC12B747ADFA38` | `R-20261118T031327Z-test-1.0.1` | D0 báo dương vì ba dấu hiệu cùng có mặt; static-only báo âm vì không có luồng tên export → hash |

D0 không bị chỉnh để bỏ sót mẫu nào. Trên tập test đề xuất, D0 không có FN.

## 9. Giới hạn đã quan sát

- Tập mẫu nhỏ, các P/E cùng một họ PoC và cùng source dùng chung. Người viết rule biết source, nên điểm số không chứng minh khả năng tổng quát.
- GCC `-O2`: hai probe `partial` do hết ngân sách ở hàm runtime. Với P1, extractor chỉ truy tới AddressOfNames sau khi resolver bị inline vào `main`.
- MSVC `/O2`: chuỗi vẫn được xác minh ở P1 và P3 dù hàm hash bị inline.
- D0-C3 phân biệt yếu vì mã khởi động CRT đã có lời gọi gián tiếp ngoài IAT.
- Hash-like loop của D0 báo nhầm trên mã runtime MinGW.
- Quét tuyến tính của D0 tính cả mã không chạy tới được, như ba lời gọi trong E1.

## 10. Giới hạn chưa kiểm tra

- Resolver tự tính địa chỉ qua AddressOfOrdinals và AddressOfFunctions, duyệt PEB, PE32, packer hoặc mã làm rối đều chưa có mẫu thử.
- Chưa có kết quả chạy thực, API trace hay dữ liệu của TV3/TV4 trong phần này.

## 11. Tái lập

Xem [README-TV2.md](../../README-TV2.md).
