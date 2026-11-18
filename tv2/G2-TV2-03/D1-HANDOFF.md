# Gói bàn giao static features cho D1

**Đây là đề xuất của TV2.** Repository chưa có giao diện D1. Việc tạo được bản ghi dưới đây không có nghĩa D1 đã được tích hợp.

## Thành phần

| Thành phần | Đường dẫn |
|---|---|
| Features đầy đủ | `schemas/tv2/static-features-1.0.schema.json` |
| Bản ghi phẳng cho D1 | `schemas/tv2/d1-static-input-1.0.schema.json` |
| Adapter | `detectors/tv2/tv2d1adapter.py` |
| Bản ghi tập phát triển | `evidence/G2/TV2/G2-TV2-03/d1-input-dev/` |
| Phiên bản khóa | `configs/tv2/locks/rule-lock-1.0.1.json` |

## Quy ước giá trị

- Quan hệ: `verified = 1.0`, `heuristic = 0.5`, `absent = 0.0`.
- `unknown` và `analysis_error` thành `null`, đồng thời tên trường nằm trong `missing`.
- Giá trị `0.5` chỉ là mã hóa thứ bậc do TV2 đề xuất, không phải xác suất.
- Mọi bản ghi có `sha256`, `analysis_id` và `features_content_sha256` để truy về features gốc.

## Cách tạo

```powershell
artifacts\tools\venv\Scripts\python.exe detectors\tv2\tv2d1adapter.py <features.json> --out-dir <thư mục>
```

## Câu hỏi cần nhóm chốt

1. D1 nhận JSON từng mẫu hay một bảng gộp?
2. D1 xử lý `null` thế nào? Không được tự coi là benign.
3. Static-only trong đánh giá nhóm có đúng là rule `SR-R1` không?
4. Split chính thức do TV4 công bố ở đâu?
