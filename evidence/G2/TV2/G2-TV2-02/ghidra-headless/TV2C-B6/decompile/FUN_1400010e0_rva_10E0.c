
char * FUN_1400010e0(short *param_1,char *param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  char *_Str1;
  uint local_48;
  
  if ((*param_1 == 0x5a4d) &&
     (*(int *)((longlong)param_1 + (longlong)*(int *)(param_1 + 0x1e)) == 0x4550)) {
    uVar1 = ((int *)((longlong)param_1 + (longlong)*(int *)(param_1 + 0x1e)))[0x22];
    uVar2 = *(uint *)((longlong)param_1 + (ulonglong)uVar1 + 0x20);
    for (local_48 = 0; local_48 < *(uint *)((longlong)param_1 + (ulonglong)uVar1 + 0x18);
        local_48 = local_48 + 1) {
      _Str1 = (char *)((longlong)param_1 +
                      (ulonglong)
                      *(uint *)((longlong)param_1 + (ulonglong)local_48 * 4 + (ulonglong)uVar2));
      iVar3 = strcmp(_Str1,param_2);
      if (iVar3 == 0) {
        return _Str1;
      }
    }
  }
  return (char *)0x0;
}


