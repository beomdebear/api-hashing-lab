
/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */

uint FUN_1400013f0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  DWORD DVar1;
  undefined8 uVar2;
  int *piVar3;
  undefined1 auStack_c8 [32];
  undefined8 local_a8;
  undefined4 local_a0;
  undefined8 local_98;
  uint local_88;
  uint local_84;
  uint local_80;
  int local_7c;
  HMODULE local_78;
  int local_70;
  int local_6c;
  longlong local_68;
  code *local_60;
  code *local_58;
  code *local_50;
  uint local_48 [4];
  int local_38 [4];
  code *local_28 [3];
  ulonglong local_10;
  
  local_10 = DAT_1400040c0 ^ (ulonglong)auStack_c8;
  local_7c = 0;
  local_88 = 0;
  local_28[0] = (code *)0x0;
  local_28[1] = (code *)0x0;
  local_28[2] = (code *)0x0;
  local_38[0] = -0x146939f0;
  local_38[1] = 0x663cecb0;
  local_38[2] = 0x3870ca07;
  local_48[0] = 0;
  local_48[1] = 1;
  local_48[2] = 2;
  local_78 = LoadLibraryW(u_kernel32_dll_140004000);
  if (local_78 == (HMODULE)0x0) {
    DVar1 = GetLastError();
    FUN_1400016e0(s_Load_failed___lu_140004020,(ulonglong)DVar1,param_3,param_4);
    local_88 = 0xe;
  }
  else {
    for (local_84 = 0; local_84 < 3; local_84 = local_84 + 1) {
      local_80 = local_48[local_84];
      local_88 = FUN_140001360(local_78,local_38[local_80],(longlong *)(local_28 + local_80));
      if (local_88 != 0) {
        FUN_1400016e0(s_Resolve_slot__u_failed___d_140004038,(ulonglong)local_80,(ulonglong)local_88
                      ,param_4);
        FreeLibrary(local_78);
        return local_88;
      }
      local_88 = 0;
    }
    local_60 = local_28[0];
    local_58 = local_28[1];
    local_50 = local_28[2];
    local_98 = 0;
    local_a0 = 0x80;
    local_a8 = CONCAT44(local_a8._4_4_,1);
    piVar3 = (int *)0x0;
    uVar2 = 0;
    local_68 = (*local_28[0])(u_marker_txt_140004058,0x40000000);
    if (local_68 == -1) {
      DVar1 = GetLastError();
      FUN_1400016e0(s_Create_failed___lu_140004070,(ulonglong)DVar1,uVar2,piVar3);
      local_88 = 0x1e;
    }
    else {
      local_a8 = 0;
      piVar3 = &local_7c;
      uVar2 = 0x10;
      local_70 = (*local_58)(local_68,s_D08_LAB_MARKER_140004088);
      local_6c = (*local_50)(local_68);
      if ((local_70 == 0) || (local_7c != 0x10)) {
        local_88 = 0x1f;
      }
      else if (local_6c == 0) {
        local_88 = 0x20;
      }
    }
    FreeLibrary(local_78);
    FUN_1400016e0(s_Marker_task_exit___d_1400040a0,(ulonglong)local_88,uVar2,piVar3);
  }
  return local_88;
}


