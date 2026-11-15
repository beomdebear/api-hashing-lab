# Checklist TV1

Đánh dấu sau khi đã có kết quả thực tế, không đánh dấu chỉ vì nhận được mã mẫu.

- [ ] G1-TV1-01: VM x64, compiler, environment.md, snapshot và ảnh.
- [ ] G1-TV1-02: B1/B2 tạo marker, có imports/strings, source commit, build/run logs.
- [ ] G1-TV1-03: P1 chạy đúng; audit xác nhận tên/địa chỉ; giải thích được vòng hash.
- [ ] G2-TV1-01: P2/P3 chạy đúng; cấu hình và bảng hash; audit 3 thuật toán.
- [ ] G2-TV1-02: P4/P5 chạy đúng; E1/E2 dừng đúng; log/ảnh/bảng khác biệt đầy đủ.
- [ ] G2-TV1-03: kiểm tra ba lần, không ghi đè, collision; bàn giao đúng SHA-256 và commit.
- [ ] G3-TV1-01: lỗi mẫu được phân biệt với lỗi collector/detector; có hồ sơ điều tra.
- [ ] G3-TV1-02: viết phần cơ chế; sơ đồ/ảnh thật; demo và video thử.
- [ ] G3-TV1-03: build cuối, checklist review TV2, source/config/binary/bằng chứng đồng bộ.

Collision audit phải chạy trên DLL thật của VM. matches=1 chỉ khẳng định không trùng đối với
ba hash mục tiêu trên module/phiên bản Windows đã kiểm tra; không chứng minh hàm hash không có collision.

## Mẫu README minh chứng cho một bước

- Mã công việc:
- Người làm / người review:
- Ngày thực hiện:
- Source commit:
- Sample ID / SHA-256:
- Windows / compiler / flags:
- Run ID và lệnh/thao tác:
- Kết quả mong đợi:
- Kết quả thực tế:
- Đường dẫn log, ảnh, file kết quả:
- Giải thích từng ảnh:
- Lỗi hoặc giới hạn còn lại:
- Kết luận nghiệm thu:
