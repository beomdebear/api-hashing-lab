
uint FUN_140001000(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  DWORD DVar1;
  HMODULE hModule;
  INT_PTR IVar2;
  undefined8 uVar3;
  int *piVar4;
  undefined8 in_stack_ffffffffffffff98;
  undefined4 uVar5;
  uint local_48;
  int local_38;
  int local_34;
  int local_30;
  INT_PTR local_28;
  FARPROC local_20;
  FARPROC local_18;
  FARPROC local_10;
  
  uVar5 = (undefined4)((ulonglong)in_stack_ffffffffffffff98 >> 0x20);
  local_38 = 0;
  local_48 = 0;
  hModule = LoadLibraryW(u_kernel32_dll_140003000);
  if (hModule == (HMODULE)0x0) {
    DVar1 = GetLastError();
    FUN_140001220(s_Load_failed___lu_140003020,(ulonglong)DVar1,param_3,param_4);
    local_48 = 0xe;
  }
  else {
    local_20 = GetProcAddress(hModule,s_CreateFileW_140003038);
    local_18 = GetProcAddress(hModule,s_WriteFile_140003048);
    local_10 = GetProcAddress(hModule,s_CloseHandle_140003058);
    if (((local_20 == (FARPROC)0x0) || (local_18 == (FARPROC)0x0)) || (local_10 == (FARPROC)0x0)) {
      FreeLibrary(hModule);
      puts(s_Resolve_failed__140003068);
      local_48 = 0xd;
    }
    else {
      piVar4 = (int *)0x0;
      uVar3 = 0;
      local_28 = (*local_20)(u_marker_txt_140003078,0x40000000,0,0,CONCAT44(uVar5,1),0x80,0);
      if (local_28 == -1) {
        DVar1 = GetLastError();
        FUN_140001220(s_Create_failed___lu_140003090,(ulonglong)DVar1,uVar3,piVar4);
        local_48 = 0x1e;
      }
      else {
        piVar4 = &local_38;
        uVar3 = 0x10;
        IVar2 = (*local_18)(local_28,s_D08_LAB_MARKER_1400030a8,0x10,piVar4,0);
        local_34 = (int)IVar2;
        IVar2 = (*local_10)(local_28);
        local_30 = (int)IVar2;
        if ((local_34 == 0) || (local_38 != 0x10)) {
          local_48 = 0x1f;
        }
        else if (local_30 == 0) {
          local_48 = 0x20;
        }
      }
      FreeLibrary(hModule);
      FUN_140001220(s_Marker_task_exit___d_1400030c0,(ulonglong)local_48,uVar3,piVar4);
    }
  }
  return local_48;
}


