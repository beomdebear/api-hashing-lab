
uint FUN_140001140(void)

{
  uint uVar1;
  HMODULE hModule;
  FARPROC pFVar2;
  FARPROC pFVar3;
  FARPROC pFVar4;
  undefined8 in_R9;
  
  uVar1 = FUN_1400010e0((byte *)"mode=marker;version=1");
  if (uVar1 == 0xb5941732) {
    hModule = LoadLibraryW(u_kernel32_dll_140003050);
    if (hModule == (HMODULE)0x0) {
      uVar1 = 0xe;
    }
    else {
      pFVar2 = GetProcAddress(hModule,s_CreateFileW_140003070);
      pFVar3 = GetProcAddress(hModule,s_WriteFile_140003080);
      pFVar4 = GetProcAddress(hModule,s_CloseHandle_140003090);
      if (((pFVar2 == (FARPROC)0x0) || (pFVar3 == (FARPROC)0x0)) || (pFVar4 == (FARPROC)0x0)) {
        FreeLibrary(hModule);
        uVar1 = 0xd;
      }
      else {
        uVar1 = FUN_140001000(pFVar2,pFVar3,pFVar4);
        FreeLibrary(hModule);
        FUN_1400012a0(s_Marker_task_exit___d_1400030a0,(ulonglong)uVar1,pFVar4,in_R9);
      }
    }
  }
  else {
    puts(s_Config_integrity_check_failed__140003030);
    uVar1 = 0x28;
  }
  return uVar1;
}


