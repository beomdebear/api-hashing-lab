# Kiểm tra cuối phần TV2

Thời điểm: 2026-11-18T10:50:09+07:00. Sinh bởi `detectors/tv2/tv2linkcheck.py`.

| Mục | Kết quả |
|---|---|
| Tài liệu đã quét | 43 |
| Liên kết nội bộ đã kiểm | 98 |
| Đường dẫn trong mã đã kiểm | 277 |
| Run phiên bản hiện tại | `R-20261118T031326Z-dev-1.0.1`, `R-20261118T031327Z-test-1.0.1`, `R-20261118T031328Z-probe-1.0.1` |
| Lock hiện tại | `configs/tv2/locks/rule-lock-1.0.1.json` |
| Commit khóa | `1befa67` chứa đúng các tệp của lock |
| Ảnh GUI đã có | 0 |
| Ảnh GUI còn thiếu | 22 |
| Lỗi liên kết hoặc phiên bản | 0 |

## Checklist

- [x] Code, config, schema, manifest và nhãn đề xuất khớp lock 1.0.1.
- [x] Mọi run hiện tại dùng đúng code, config và được báo cáo nêu.
- [x] Liên kết và đường dẫn trong tài liệu TV2 tồn tại.
- [ ] Đủ ảnh GUI theo danh sách chụp.
- [x] Có commit chứa đúng các tệp của lock.
- [ ] TV1 phản hồi review.
- [ ] TV4 xác nhận mẫu đối chứng, nhãn và split.
- [ ] Có bảng D0/D1 thực đo.

## Lỗi đã sửa trong phiên

- Extractor 1.0.0 dừng vì số dịch âm; sửa ở 1.0.1 và thêm test.
- Lỗi nội bộ của extractor từng có thể dừng cả lượt chạy; nay trả `analysis_error`.
- Bảng B1/B2 ban đầu chưa phân biệt chuỗi của bảng import với chuỗi được mã tham chiếu; đã sửa.
- Kết luận về GCC và `/O2` ban đầu chưa đủ căn cứ; đã kiểm bằng symbol và sự kiện phân tích.
- Script Ghidra ban đầu dùng API chuỗi cũ, xem `INT3` là lời gọi gián tiếp và không nhập lại được sau lần lỗi; đã sửa.

## Còn tồn đọng

- Hai probe GCC vượt ngân sách phân tích; chưa sửa để giữ nguyên phiên bản đã đánh giá.
- Script chụp GUI chưa được chạy với giao diện thật.

## Ảnh còn thiếu

- evidence/G1/TV2/G1-TV2-02/images/B1-imports.png
- evidence/G1/TV2/G1-TV2-02/images/B1-strings.png
- evidence/G1/TV2/G1-TV2-02/images/B1-calls.png
- evidence/G1/TV2/G1-TV2-02/images/B2-imports.png
- evidence/G1/TV2/G1-TV2-02/images/B2-strings.png
- evidence/G1/TV2/G1-TV2-02/images/B2-calls.png
- evidence/G1/TV2/G1-TV2-03/images/P1-1-hash-loop.png
- evidence/G1/TV2/G1-TV2-03/images/P1-2-export-hash-compare.png
- evidence/G1/TV2/G1-TV2-03/images/P1-3-resolve.png
- evidence/G1/TV2/G1-TV2-03/images/P1-4-pointer-use.png
- evidence/G2/TV2/G2-TV2-01/images/P1-D0-C1-imports.png
- evidence/G2/TV2/G2-TV2-01/images/P1-D0-C2-hash-loop.png
- evidence/G2/TV2/G2-TV2-01/images/P1-D0-C3-indirect-call.png
- evidence/G2/TV2/G2-TV2-02/images/B3-name-table.png
- evidence/G2/TV2/G2-TV2-02/images/B4-data-hash.png
- evidence/G2/TV2/G2-TV2-02/images/B4-static-imports.png
- evidence/G2/TV2/G2-TV2-02/images/B6-export-strcmp.png
- evidence/G2/TV2/G2-TV2-02/images/B6-resolve.png
- evidence/G3/TV2/G3-TV2-01/images/B5-FP-D0-C1-imports.png
- evidence/G3/TV2/G3-TV2-01/images/B5-FP-D0-C2-hash-loop.png
- evidence/G3/TV2/G3-TV2-01/images/B5-FP-D0-resolve-by-name.png
- evidence/G3/TV2/G3-TV2-01/images/B5-FP-D0-C3-indirect-call.png
