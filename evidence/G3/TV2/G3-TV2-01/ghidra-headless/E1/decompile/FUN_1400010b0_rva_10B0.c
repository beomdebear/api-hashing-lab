
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
                       (ulonglong)
                       *(uint *)((longlong)param_1 + (ulonglong)local_48 * 4 + (ulonglong)uVar2));
        pvVar5 = memchr(_Buf,0,(ulonglong)
                               (uVar1 - *(int *)((longlong)param_1 +
                                                (ulonglong)local_48 * 4 + (ulonglong)uVar2)));
        if (pvVar5 == (void *)0x0) {
          return 0xc;
        }
        iVar3 = FUN_140001000(_Buf);
        if (iVar3 == param_2) {
          *param_4 = *param_4 + 1;
          *param_3 = _Buf;
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


