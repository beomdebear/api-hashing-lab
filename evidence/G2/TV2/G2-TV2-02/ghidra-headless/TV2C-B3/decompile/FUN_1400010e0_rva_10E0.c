
/* WARNING: Function: __security_check_cookie replaced with injection: security_check_cookie */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

uint FUN_1400010e0(void)

{
  FARPROC pFVar1;
  undefined *puVar2;
  undefined8 in_R9;
  undefined1 auStack_68 [32];
  uint local_48;
  uint local_44;
  HMODULE local_40;
  undefined8 local_38;
  undefined *local_30 [3];
  ulonglong local_18;
  
  local_18 = DAT_1400040c0 ^ (ulonglong)auStack_68;
  local_30[0] = (undefined *)0x0;
  local_30[1] = (undefined *)0x0;
  local_30[2] = (undefined *)0x0;
  local_40 = GetModuleHandleW(u_kernel32_dll_140004060);
  if (local_40 == (HMODULE)0x0) {
    local_44 = 0xe;
  }
  else {
    for (local_48 = 0; local_48 < 3; local_48 = local_48 + 1) {
      pFVar1 = GetProcAddress(local_40,(&PTR_s_CreateFileW_140003240)[local_48]);
      local_30[local_48] = pFVar1;
      if (local_30[local_48] == (undefined *)0x0) {
        return 0xd;
      }
    }
    local_38 = 0;
    puVar2 = local_30[2];
    local_44 = FUN_140001000(local_30[0],local_30[1],local_30[2]);
    FUN_140001250(s_Marker_task_exit___d_140004080,(ulonglong)local_44,puVar2,in_R9);
  }
  return local_44;
}


