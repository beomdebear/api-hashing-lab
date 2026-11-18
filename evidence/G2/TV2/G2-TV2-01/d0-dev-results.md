# Kết quả D0 trên tập phát triển

Run: `R-20261118T031326Z-dev-1.0.1`. Nhãn là đề xuất của TV2, chỉ evaluator đọc.

| Mẫu | Sample ID | SHA-256 | Nhãn đề xuất | Kết luận | KQ | Lý do | Bằng chứng đầu | ms |
|---|---|---|---|---|---|---|---|---|
| P1 | S-0277D53B11 | 0277D53B1124978B… | positive | positive | TP | all conditions passed: D0-C1, D0-C2, D0-C3 | D0-C3 RVA 0x15B1: call qword ptr [rsp + 0x68] | 125.2 |
| B1 | S-1B52E1BC5C | 1B52E1BC5C2CA66B… | negative | negative | TN | failed conditions: D0-C1, D0-C2 | D0-C3 RVA 0x135E: call qword ptr [rip + 0xe5c] | 33.6 |
| B2 | S-4332381DAC | 4332381DAC194876… | negative | negative | TN | failed conditions: D0-C2 | D0-C3 RVA 0x1102: call qword ptr [rsp + 0x68] | 31.7 |
| TV2C-B3 | S-DAA4113A94 | DAA4113A94D76812… | negative | negative | TN | failed conditions: D0-C2 | D0-C3 RVA 0x1046: call qword ptr [rsp + 0x70] | 60.2 |
| TV2C-B4 | S-DCD2080F7D | DCD2080F7D406A4D… | negative | negative | TN | failed conditions: D0-C1 | D0-C3 RVA 0x13AE: call qword ptr [rip + 0xe04] | 33.6 |

## Vị trí bằng chứng của P1

| Điều kiện | Đặc trưng | RVA | Quan sát | Ghi chú |
|---|---|---|---|---|
| D0-C1 | f.imports.get_proc_address | 0x3010 | `KERNEL32.dll!GetProcAddress` | import address table slot |
| D0-C2 | f.code.hash_like_loops | 0x101F | `movzx eax, byte ptr [rax]` | byte load inside loop |
| D0-C2 | f.code.hash_like_loops | 0x1026 | `imul eax, dword ptr [rsp], 0x21` | mixing instruction inside loop |
| D0-C2 | f.code.hash_like_loops | 0x1032 | `add eax, ecx` | combining instruction inside loop |
| D0-C2 | f.code.hash_like_loops | 0x1044 | `jmp 0x14000101a` | loop back edge |
| D0-C3 | f.code.non_import_indirect_calls | 0x15B1 | `call qword ptr [rsp + 0x68]` | indirect call whose target is not an import slot |
| D0-C3 | f.code.non_import_indirect_calls | 0x1600 | `call qword ptr [rsp + 0x70]` | indirect call whose target is not an import slot |
| D0-C3 | f.code.non_import_indirect_calls | 0x160D | `call qword ptr [rsp + 0x78]` | indirect call whose target is not an import slot |
| D0-C3 | f.code.non_import_indirect_calls | 0x1996 | `call qword ptr [rip + 0x183c]` | indirect call whose target is not an import slot |
