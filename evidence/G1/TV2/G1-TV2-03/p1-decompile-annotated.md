# Decompile P1 có chú thích (bản văn bản)

Mã dưới đây do decompiler Ghidra 12.2 xuất ở chế độ headless. Dòng `// [TV2]` do script TV2 chèn. **Đây không phải ảnh GUI.**

## Vòng hash — `FUN_140001000`

```c
int FUN_140001000(byte *param_1)

{
  int local_18;
  byte *local_10;
  
  local_18 = 0x1505;
  // [TV2] seed DJB2 = 5381
  for (local_10 = param_1; *local_10 != 0; local_10 = local_10 + 1) {
    local_18 = local_18 * 0x21 + (uint)*local_10;
    // [TV2] h = h * 33 + byte
  }
  return local_18;
}
```

## Duyệt export và so sánh — `FUN_1400010b0`

```c
undefined8 FUN_1400010b0(short *param_1,int param_2,undefined8 *param_3,int *param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  ulonglong uVar4;
  void *pvVar5;
  int *piVar6;
  byte *_Buf;
  uint local_48;
  uint local_38;
  uint uStack_34;
  
  *param_3 = 0;
  *param_4 = 0;
  if (((((param_1 != (short *)0x0) && (*param_1 == 0x5a4d)) && (0 < *(int *)(param_1 + 0x1e))) &&
      ((piVar6 = (int *)((longlong)param_1 + (longlong)*(int *)(param_1 + 0x1e)), *piVar6 == 0x4550
       && ((short)piVar6[6] == 0x20b)))) && (piVar6[0x21] != 0)) {
    uVar1 = piVar6[0x14];
    uVar4 = *(ulonglong *)(piVar6 + 0x22);
    local_38 = (uint)uVar4;
    if (((local_38 != 0) && (uStack_34 = (uint)(uVar4 >> 0x20), 0x27 < uStack_34)) &&
       (iVar3 = FUN_140001060(local_38,(ulonglong)uStack_34,uVar1), iVar3 != 0)) {
      uVar4 = uVar4 & 0xffffffff;
      if ((*(int *)((longlong)param_1 + uVar4 + 0x20) == 0) ||
         (iVar3 = FUN_140001060(*(uint *)((longlong)param_1 + uVar4 + 0x20),
                                (ulonglong)*(uint *)((longlong)param_1 + uVar4 + 0x18) << 2,uVar1),
         iVar3 == 0)) {
        return 0xc;
      }
      uVar2 = *(uint *)((longlong)param_1 + uVar4 + 0x20);
      for (local_48 = 0; local_48 < *(uint *)((longlong)param_1 + uVar4 + 0x18);
          local_48 = local_48 + 1) {
        iVar3 = FUN_140001060(*(uint *)((longlong)param_1 +
                                       (ulonglong)local_48 * 4 + (ulonglong)uVar2),1,uVar1);
        if (iVar3 == 0) {
          return 0xc;
        }
        _Buf = (byte *)((longlong)param_1 +
        // [TV2] con trỏ tên export = module base + RVA tên
                       (ulonglong)
                       *(uint *)((longlong)param_1 + (ulonglong)local_48 * 4 + (ulonglong)uVar2));
        pvVar5 = memchr(_Buf,0,(ulonglong)
                               (uVar1 - *(int *)((longlong)param_1 +
                                                (ulonglong)local_48 * 4 + (ulonglong)uVar2)));
        if (pvVar5 == (void *)0x0) {
          return 0xc;
        }
        iVar3 = FUN_140001000(_Buf);
        // [TV2] hash tên export
        if (iVar3 == param_2) {
        // [TV2] so hash với giá trị đích
          *param_4 = *param_4 + 1;
          *param_3 = _Buf;
          // [TV2] ghi tên được chọn ra tham số out
        }
      }
      if (*param_4 == 0) {
        return 10;
      }
      if (*param_4 == 1) {
        return 0;
      }
      *param_3 = 0;
      return 0xb;
    }
  }
  return 0xc;
}
```

## Resolve — `FUN_140001360`

```c
int FUN_140001360(HMODULE param_1,int param_2,longlong *param_3)

{
  undefined8 uVar1;
  FARPROC pFVar2;
  int local_24;
  int local_20 [2];
  LPCSTR local_18 [3];
  
  *param_3 = 0;
  uVar1 = FUN_1400010b0((short *)param_1,param_2,local_18,local_20);
  local_24 = (int)uVar1;
  if (local_24 == 0) {
    pFVar2 = GetProcAddress(param_1,local_18[0]);
    // [TV2] tên đã chọn đi vào GetProcAddress
    *param_3 = (longlong)pFVar2;
    if (*param_3 == 0) {
      local_24 = 0xd;
    }
    else {
      local_24 = 0;
    }
  }
  return local_24;
}
```
