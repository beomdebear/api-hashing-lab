# Review phần PoC của TV1

Người thực hiện: AI hỗ trợ TV2. **TV1 chưa phản hồi**, nên đây chưa phải review đã được hai bên chốt. Không có tệp TV1 nào bị sửa.
Binary kiểm tra: build `20261118-094956` do TV2 build lại từ source hiện tại, không phải binary lịch sử của TV1.

## Đối chiếu mô tả với binary

| Mô tả được kiểm | Nguồn | Bằng chứng trên binary | Kết quả |
|---|---|---|---|
| P1 dùng DJB2, seed 5381, h*33+byte | `docs/TV1-HUONG-DAN.md` mục 3 | `RVA_00001009  MOV dword ptr [RSP],0x1505`; `RVA_00001026  IMUL EAX,dword ptr [RSP],0x21` | Khớp |
| P2 dùng FNV-1a | `docs/TV1-HUONG-DAN.md` mục 4 | `RVA_00001009  MOV dword ptr [RSP],0x811c9dc5`; `RVA_00001045  IMUL EAX,dword ptr [RSP],0x1000193` | Khớp |
| P3 dùng CRC32 phản chiếu | `docs/TV1-HUONG-DAN.md` mục 4 | `RVA_0000106A  MOV dword ptr [RSP + 0x8],0xedb88320` | Khớp |
| P4 đổi seed thành 1337 | `docs/TV1-HUONG-DAN.md` mục 5 | `RVA_00001009  MOV dword ptr [RSP],0x539` | Khớp |
| P5 đổi thứ tự resolve | `samples/common/tv1_program.h` | Thứ tự slot P1 = ['0x0', '0x1', '0x2'], P5 = ['0x1', '0x2', '0x0'] | Khớp |
| E1 đổi bit cao của hash CreateFileW | `docs/TV1-HUONG-DAN.md` mục 6 | `RVA_000014CE  MOV EDX,0x6b96c610` | Khớp |
| E2 dừng sớm nhưng giữ đường hashing | `docs/TV1-HUONG-DAN.md` mục 6 | `--continue` tham chiếu tại 0x254 0x149B; `strcmp` tại 0x14AE; chuỗi quan hệ tới resolve đã xác minh: True | Khớp |
| GetProcAddress nhận tên, không nhận hash | `docs/TV1-HUONG-DAN.md` mục 3 | P1 + 0x13A7 nạp RDX từ biến tên, P1 + 0x13B1 gọi GetProcAddress | Khớp |
| Không nhúng tên API đích trong P1 | `docs/TV1-HUONG-DAN.md` mục 3 | Không có ASCII/UTF-16 của ba tên trong file: True; không import ba API này: True | Khớp |
| Duyệt hết tên export để phát hiện collision | `samples/common/tv1_resolver.h` | Sau khi ghi tên, mã vẫn quay lại vòng lặp: `RVA_0000130E  JMP 0x140001246` | Khớp |
| Không duyệt PEB, không tự tính địa chỉ qua AddressOfFunctions | `docs/TV1-HUONG-DAN.md` phần giới hạn | Truy cập GS trong các hàm đã xuất: 0; đọc export +0x1C hoặc +0x24 trong hàm tìm tên: 0 | Khớp |

## Điểm đề nghị TV1 xem

| Mức | Vị trí | Nhận xét | Đề xuất |
|---|---|---|---|
| Nên sửa | `samples/common/tv1_resolver.h:8` | Chú thích nói chỉ chấp nhận system DLL hợp lệ, nhưng mã chỉ kiểm tra cấu trúc PE. Việc dùng kernel32 do nơi gọi quyết định. | Sửa chú thích thành điều kiện thực tế của tham số. |
| Nên sửa | `docs/TV1-HUONG-DAN.md:87` | Câu GetProcAddress nhận TÊN đúng với PoC nhưng chưa đủ với API. | Ghi: API nhận tên hoặc ordinal; PoC truyền tên đã tìm được. |
| Nên sửa | `README-TV1.md:19` | Mục trạng thái mô tả lúc tạo gói nên ghi chưa build bằng MSVC, trong khi `evidence/G1/TV1/` đã có kết quả correctness và audit. | Bổ sung trạng thái hiện tại để người đọc không hiểu nhầm. |
| Nên sửa | `evidence/G1/TV1/G1-TV1-03/README.md` | README ghi chưa thực hiện, nhưng cùng thư mục đã có CSV kết quả. | TV1 điền README hoặc ghi rõ phần chưa đạt. |
| Cần phối hợp | `evidence/G1/TV1/G1-TV1-03/P1-correctness-summary.csv` | P1 lịch sử có SHA-256 `DDFB2A29…`, còn build TV2 là `0277D53B…`. Hai bản không được trộn địa chỉ. | TV1 bàn giao binary và commit chốt để TV2 chạy lại. |
| Ghi nhận | `scripts/tv1-build.ps1:49` | Trường `build_flags` trong manifest bỏ sót `/utf-8` và `/INCREMENTAL:NO` đang được dùng. | Ghi đủ cờ để tái lập. |
| Ghi nhận | `samples/common/tv1_program.h` | Với E1, MSVC báo C4702 (6 cảnh báo) và vẫn sinh đoạn mã không chạy tới. Công cụ quét tuyến tính sẽ thấy các lời gọi gián tiếp trong đoạn đó. | Nêu trong báo cáo khi so sánh công cụ. |

## Phạm vi chưa kiểm

- Không chạy các binary, nên chưa kiểm hành vi runtime, địa chỉ forwarded export hay collision trên DLL thật.
- Chưa đối chiếu với collector của TV3.
