# Dấu hiệu và kết quả ban đầu của các mẫu đối chứng đề xuất

`TV2C-B3..B6` là mẫu do TV2 đề xuất cho vai trò B3–B6. **TV4 chưa xác nhận**, nên đây chưa phải B3–B6 chính thức.

| Mẫu | Vai trò đề xuất | SHA-256 | Import GetProcAddress | Vòng giống hash | Gọi gián tiếp ngoài IAT | Duyệt tên export | Tên export → hash | D0 | Static-only |
|---|---|---|---|---|---|---|---|---|---|
| TV2C-B3 | B3: resolve theo tên từ bảng chuỗi | DAA4113A94D76812… | có | 0 | 6 | không thấy | không thấy | negative (TN) | negative (TN) |
| TV2C-B4 | B4: hash dữ liệu, API là import sẵn | DCD2080F7D406A4D… | không | 1 | 3 | không thấy | không thấy | negative (TN) | negative (TN) |
| TV2C-B5 | B5: hash cấu hình, resolve theo hằng chuỗi | EB8A4426E124E966… | có | 1 | 6 | không thấy | không thấy | positive (FP) | negative (TN) |
| TV2C-B6 | B6: duyệt export, so bằng strcmp, resolve theo tên | 6E7DCBA2D1CAAA8E… | có | 0 | 6 | đã xác minh | không thấy | negative (TN) | negative (TN) |

## FP/FN ban đầu của D0

- FP: `TV2C-B5`. Ba dấu hiệu của D0 cùng tồn tại nhưng không liên quan với nhau.
- FN trên bốn mẫu đối chứng: không áp dụng, vì cả bốn đều mang nhãn âm tính đề xuất.
- `TV2C-B6` không bị D0 báo vì so tên bằng `strcmp` qua import, nên không tạo vòng giống hash.

## Kiểm tra điều kiện của PDF trên binary

| Mẫu | Số lời gọi GetProcAddress | Tên hằng đã truy được | Lời gọi có tên không phải hằng | Vòng giống hash | Tên chọn bằng hash → resolve |
|---|---|---|---|---|---|
| TV2C-B3 | 1 | 0 | 1 | 0 | không thấy |
| TV2C-B4 | 0 | 0 | 0 | 1 | không thấy |
| TV2C-B5 | 3 | 3 | 0 | 1 | không thấy |
| TV2C-B6 | 1 | 0 | 1 | 0 | không thấy |

Với TV2C-B3, tên được đọc từ bảng con trỏ nên extractor không truy được thành hằng chuỗi trực tiếp. Ghidra cho thấy các chuỗi tên API được bảng dữ liệu tham chiếu: CreateFileW @0x4000 (tham chiếu: 0x25C 0x3240); WriteFile @0x4010 (tham chiếu: 0x3248); CloseHandle @0x4020 (tham chiếu: 0x3250).
