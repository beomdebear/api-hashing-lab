
/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */

undefined8
FUN_1400013f0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  DWORD DVar1;
  undefined8 uVar2;
  longlong *plVar3;
  undefined1 auStack_c8 [64];
  uint local_88;
  undefined4 local_84;
  HMODULE local_80;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  longlong local_30 [6];
  
  local_30[3] = DAT_140004100 ^ (ulonglong)auStack_c8;
  local_84 = 0;
  local_88 = 0;
  local_30[0] = 0;
  local_30[1] = 0;
  local_30[2] = 0;
  local_50 = 0xeb96c610;
  local_4c = 0x663cecb0;
  local_48 = 0x3870ca07;
  local_40 = 0;
  local_3c = 1;
  local_38 = 2;
  local_80 = LoadLibraryW(u_kernel32_dll_140004000);
  if (local_80 == (HMODULE)0x0) {
    DVar1 = GetLastError();
    FUN_140001680(s_Load_failed___lu_140004020,(ulonglong)DVar1,param_3,param_4);
    uVar2 = 0xe;
  }
  else {
    plVar3 = local_30;
    local_88 = FUN_140001360(local_80,0x6b96c610,plVar3);
    FreeLibrary(local_80);
    if (local_88 == 10) {
      puts(s_Wrong_hash_not_found__140004038);
      uVar2 = 10;
    }
    else {
      FUN_140001680(s_Unexpected_wrong_hash_outcome____140004050,(ulonglong)local_88,plVar3,param_4)
      ;
      uVar2 = 0x15;
    }
  }
  return uVar2;
}


