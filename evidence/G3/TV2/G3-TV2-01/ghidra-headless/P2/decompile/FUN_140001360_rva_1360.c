
int FUN_140001360(HMODULE param_1,uint param_2,longlong *param_3)

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


