# Rule D0

Cấu hình: `configs/tv2/d0.json`, detector `D0`, phiên bản `1.0.0`, rule `D0-R1`.

D0 là baseline đồng xuất hiện. Kết luận `positive` khi **cả ba** điều kiện đúng trong cùng một binary:

| Điều kiện | Đặc trưng | Định nghĩa chính xác |
|---|---|---|
| `D0-C1` | `f.imports.get_proc_address` | Bảng import có hàm tên `GetProcAddress` |
| `D0-C2` | `f.code.hash_like_loops >= 1` | Có cạnh nhảy lùi trong một hàm, và đoạn từ đích nhảy tới cạnh đó chứa đủ: `movzx`/`movsx` nạp 1 byte từ bộ nhớ; một lệnh trộn `imul`, `mul`, `rol`, `ror`, `shl` hoặc `shr`; một lệnh kết hợp `add` hoặc `xor` có hai toán hạng khác nhau và toán hạng nguồn không phải hằng |
| `D0-C3` | `f.code.non_import_indirect_calls >= 1` | Có `CALL` qua thanh ghi hoặc bộ nhớ mà đích không phải ô IAT |

## Kết luận

- `positive`: cả ba điều kiện đúng.
- `negative`: ít nhất một điều kiện sai và phân tích hoàn tất.
- `unknown`: tệp lỗi, không hỗ trợ, thiếu dữ liệu, hoặc phân tích `partial` mà chưa thể kết luận dương.

## Dữ liệu đầu vào

D0 chỉ đọc tài liệu features sinh từ byte của binary. Nó không đọc nhãn, tên tệp, thư mục, source, macro TV1, bảng hash, audit hay log correctness. SHA-256 chỉ dùng để định danh.

## Cách chạy

```powershell
artifacts\tools\venv\Scripts\python.exe detectors\tv2\tv2detect.py detect <binary> --config configs\tv2\d0.json -o <prediction.json>
```

## Giới hạn

- Rule không chứng minh ba dấu hiệu liên quan với nhau.
- `D0-C3` đúng cả với B1 do mã khởi động CRT.
- `D0-C2` quét cả mã runtime và đoạn mã không chạy tới được.
- Rule được chọn trên B1, B2, P1 và không chỉnh sau khi xem kết quả đối chứng hay test.

Kết quả từng mẫu: `evidence/G2/TV2/G2-TV2-01/d0-dev-results.md`.
