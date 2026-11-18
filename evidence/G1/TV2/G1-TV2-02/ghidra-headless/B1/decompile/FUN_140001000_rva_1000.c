
uint FUN_140001000(void)

{
  DWORD DVar1;
  undefined8 uVar2;
  LPDWORD lpNumberOfBytesWritten;
  uint local_28;
  DWORD local_24;
  int local_20;
  BOOL local_1c;
  HANDLE local_18;
  
  local_24 = 0;
  local_28 = 0;
  lpNumberOfBytesWritten = (LPDWORD)0x0;
  uVar2 = 0;
  local_18 = CreateFileW(u_marker_txt_140003000,0x40000000,0,(LPSECURITY_ATTRIBUTES)0x0,1,0x80,
                         (HANDLE)0x0);
  if (local_18 == (HANDLE)0xffffffffffffffff) {
    DVar1 = GetLastError();
    FUN_140001160(s_Create_failed___lu_140003018,(ulonglong)DVar1,uVar2,lpNumberOfBytesWritten);
    local_28 = 0x1e;
  }
  else {
    lpNumberOfBytesWritten = &local_24;
    uVar2 = 0x10;
    local_20 = WriteFile(local_18,s_D08_LAB_MARKER_140003030,0x10,lpNumberOfBytesWritten,
                         (LPOVERLAPPED)0x0);
    local_1c = CloseHandle(local_18);
    if ((local_20 == 0) || (local_24 != 0x10)) {
      local_28 = 0x1f;
    }
    else if (local_1c == 0) {
      local_28 = 0x20;
    }
  }
  FUN_140001160(s_Marker_task_exit___d_140003048,(ulonglong)local_28,uVar2,lpNumberOfBytesWritten);
  return local_28;
}


