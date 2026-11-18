# Phân tích kết quả và lỗi

Nhãn và split là đề xuất của TV2, chưa được TV4 duyệt. Các mẫu P1–P5, E1, E2 cùng một họ PoC và cùng cấu hình compiler, nên đây là thử nghiệm nội bộ, không phải đánh giá held-out của nhóm.

## Tổng hợp

| Tập | Detector | Số mẫu | Phân tích ok | TP | TN | FP | FN | Unknown | Precision | Recall | F1 | Trung vị ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev | d0 | 5 | 5 | 1 | 4 | 0 | 0 | 0 | 1.0 | 1.0 | 1.0 | 33.6 |
| dev | static-only | 5 | 5 | 1 | 4 | 0 | 0 | 0 | 1.0 | 1.0 | 1.0 | 33.6 |
| test | d0 | 8 | 8 | 6 | 1 | 1 | 0 | 0 | 0.8571 | 1.0 | 0.9231 | 123.7 |
| test | static-only | 8 | 8 | 6 | 2 | 0 | 0 | 0 | 1.0 | 1.0 | 1.0 | 123.7 |
| probe | d0 | 5 | 3 | 3 | 1 | 1 | 0 | 0 | 0.75 | 1.0 | 0.8571 | 147.6 |
| probe | static-only | 5 | 3 | 2 | 1 | 0 | 0 | 2 | 1.0 | 1.0 | 1.0 | 147.6 |

Lượt test với lock 1.0.0 và 1.0.1 có 0/16 kết luận khác nhau. Runs 1.0.0 được giữ nguyên trong thư mục `runs/`.

## Lỗi của tập test

| Mẫu | Detector | Loại | Vị trí bằng chứng | Vì sao sai | Phân loại nguyên nhân |
|---|---|---|---|---|---|
| TV2C-B5 | D0 | FP | Vòng hash ở FUN_1400010e0 RVA 0x1125; GetProcAddress và gọi gián tiếp ở các vị trí trong prediction gốc | D0 chỉ cần ba dấu hiệu cùng tồn tại. Vòng FNV-1a chỉ kiểm tra chuỗi cấu hình, còn tên API là hằng chuỗi. | Dự đoán sai do giới hạn của rule đồng xuất hiện |

Static-only không có FP/FN trên tập test đề xuất. Với TV2C-B5, nó báo âm tính vì binary không duyệt tên export và không có luồng tên export → hash.

## Quan sát ở mẫu thăm dò compiler (không tính vào metric chính)

| Mẫu | Sample ID | SHA-256 | Nhãn đề xuất | Kết luận | KQ | Lý do | Bằng chứng đầu | ms |
|---|---|---|---|---|---|---|---|---|
| VAR-P1-MSVC-O2 | S-0B6D9B0A45 | 0B6D9B0A45A5B3EB… | positive | positive | TP | all conditions passed: D0-C1, D0-C2, D0-C3 | D0-C3 RVA 0x1150: call qword ptr [rsp + 0x78] | 102.9 |
| VAR-B6-GCC-O2 | S-100FDF18BA | 100FDF18BAE5457E… | negative | positive | FP | all conditions passed: D0-C1, D0-C2, D0-C3 | D0-C3 RVA 0x105E: call rdi | 2309.6 |
| VAR-B6-MSVC-O2 | S-49912FB416 | 49912FB41609E306… | negative | negative | TN | failed conditions: D0-C2 | D0-C3 RVA 0x10CA: call rsi | 38.5 |
| VAR-P3-MSVC-O2 | S-ECDFF1066F | ECDFF1066F90F3D5… | positive | positive | TP | all conditions passed: D0-C1, D0-C2, D0-C3 | D0-C3 RVA 0x1150: call qword ptr [rsp + 0x78] | 147.6 |
| VAR-P1-GCC-O2 | S-F05446A569 | F05446A5690EA1B2… | positive | positive | TP | all conditions passed: D0-C1, D0-C2, D0-C3 | D0-C3 RVA 0x105E: call rdi | 2465.6 |
| VAR-P1-MSVC-O2 | S-0B6D9B0A45 | 0B6D9B0A45A5B3EB… | positive | positive | TP | all conditions passed: SR-C1, SR-C2, SR-C3, SR-C4, SR-C5 | SR-C5 RVA 0x1101: call qword ptr [rip + 0x1f09] | 102.9 |
| VAR-B6-GCC-O2 | S-100FDF18BA | 100FDF18BAE5457E… | negative | unknown | UNKNOWN | analysis_status=partial | — | 2309.6 |
| VAR-B6-MSVC-O2 | S-49912FB416 | 49912FB41609E306… | negative | negative | TN | failed conditions: SR-C1, SR-C2, SR-C3, SR-C4, SR-C5 | — | 38.5 |
| VAR-P3-MSVC-O2 | S-ECDFF1066F | ECDFF1066F90F3D5… | positive | positive | TP | all conditions passed: SR-C1, SR-C2, SR-C3, SR-C4, SR-C5 | SR-C5 RVA 0x1101: call qword ptr [rip + 0x1f09] | 147.6 |
| VAR-P1-GCC-O2 | S-F05446A569 | F05446A5690EA1B2… | positive | unknown | UNKNOWN | analysis_status=partial | — | 2465.6 |

- Hai mẫu GCC `-O2` là `partial`: extractor vượt ngân sách ở các hàm runtime `__pformat_emit_float`, `__pformat_xint.isra.0`, nên static-only trả `unknown`. Đây là giới hạn công cụ, không phải kết luận âm tính.
- `VAR-B6-GCC-O2` là FP của D0. Toàn bộ 148 vòng giống hash nằm trong 6 hàm runtime MinGW, nhiều nhất là `__gdtoa` (60), `__mingw_pformat` (39); không có vòng nào trong `main`, `find_export_name` hay `resolve_by_name`. Mẫu này không được dùng để chỉnh rule.
- `VAR-P1-GCC-O2`: GCC inline resolver vào `main` (8 vòng giống hash ở đó). Extractor chỉ truy được tới AddressOfNames (`rel.export_names_enumerated` = `heuristic`), chưa có sự kiện con trỏ tên export. Nếu bỏ giới hạn ngân sách, mẫu này có nguy cơ thành FN. Giả thuyết về cách sửa chưa được kiểm tra.
- Với MSVC `/O2`, static-only xác minh đủ chuỗi ở P1 và P3. Hàm hash đã được inline ở: VAR-P1-MSVC-O2, VAR-P3-MSVC-O2.

## Hạn chế đã đo được của D0

- Điều kiện D0-C3 phân biệt yếu: ngay B1 đã có 3 lời gọi gián tiếp ngoài IAT, đến từ mã khởi động CRT.
- Quét tuyến tính tính cả mã không chạy tới được. Ở E1, 3 lời gọi tại 0x154F, 0x159E, 0x15AB nằm trong đoạn như vậy. Ghidra không disassemble đoạn này nên đây là khác biệt duy nhất trong `ghidra-crosscheck.csv`.
- E1 có quan hệ resolve → dùng con trỏ ở mức `heuristic`, đúng với việc địa chỉ không được gọi trên đường chạy thật.

## Phân biệt nguồn lỗi

- Lỗi mẫu: không phát hiện trong phần phân tích tĩnh. Phiên này không chạy các binary.
- Lỗi công cụ: crash số dịch âm ở extractor 1.0.0 đã sửa ở 1.0.1; hai mẫu GCC vượt ngân sách vẫn còn.
- Thiếu dữ liệu: chưa có dữ liệu của TV4 và TV3 để đối chiếu FP/FN.
- Dự đoán sai: FP của D0 trên TV2C-B5.

## Dữ liệu gốc

- dev: `evidence/G2/TV2/G2-TV2-01/runs/R-20261118T031326Z-dev-1.0.1` gồm `run.json`, `features/`, `predictions/`, `per-sample.csv`, `metrics.json`.
- test: `evidence/G3/TV2/G3-TV2-01/runs/R-20261118T031327Z-test-1.0.1` gồm `run.json`, `features/`, `predictions/`, `per-sample.csv`, `metrics.json`.
- probe: `evidence/G3/TV2/G3-TV2-01/runs/R-20261118T031328Z-probe-1.0.1` gồm `run.json`, `features/`, `predictions/`, `per-sample.csv`, `metrics.json`.
