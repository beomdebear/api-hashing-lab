
uint FUN_140001060(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  uint uVar1;
  undefined8 uVar2;
  LPDWORD lpNumberOfBytesWritten;
  uint local_28;
  DWORD local_24;
  int local_20;
  BOOL local_1c;
  HANDLE local_18;
  
  local_24 = 0;
  local_28 = 0;
  uVar1 = FUN_140001000((byte *)s_D08_LAB_MARKER_140003000);
  FUN_1400011b0(s_Marker_checksum__0x_08X_140003018,(ulonglong)uVar1,param_3,param_4);
  local_18 = CreateFileW(u_marker_txt_140003038,0x40000000,0,(LPSECURITY_ATTRIBUTES)0x0,1,0x80,
                         (HANDLE)0x0);
  if (local_18 == (HANDLE)0xffffffffffffffff) {
    local_28 = 0x1e;
  }
  else {
    lpNumberOfBytesWritten = &local_24;
    uVar2 = 0x10;
    local_20 = WriteFile(local_18,s_D08_LAB_MARKER_140003050,0x10,lpNumberOfBytesWritten,
                         (LPOVERLAPPED)0x0);
    local_1c = CloseHandle(local_18);
    if ((local_20 == 0) || (local_24 != 0x10)) {
      local_28 = 0x1f;
    }
    else if (local_1c == 0) {
      local_28 = 0x20;
    }
    FUN_1400011b0(s_Marker_task_exit___d_140003068,(ulonglong)local_28,uVar2,lpNumberOfBytesWritten)
    ;
  }
  return local_28;
}


