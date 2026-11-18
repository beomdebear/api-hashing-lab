
uint FUN_140001250(void)

{
  uint uVar1;
  HMODULE hLibModule;
  FARPROC pFVar2;
  FARPROC pFVar3;
  FARPROC pFVar4;
  undefined8 in_R9;
  
  hLibModule = LoadLibraryW(u_kernel32_dll_140004030);
  if (hLibModule == (HMODULE)0x0) {
    uVar1 = 0xe;
  }
  else {
    pFVar2 = FUN_1400011f0(hLibModule,s_CreateFileW_140004050);
    pFVar3 = FUN_1400011f0(hLibModule,s_WriteFile_140004060);
    pFVar4 = FUN_1400011f0(hLibModule,s_CloseHandle_140004070);
    if (((pFVar2 == (FARPROC)0x0) || (pFVar3 == (FARPROC)0x0)) || (pFVar4 == (FARPROC)0x0)) {
      FreeLibrary(hLibModule);
      uVar1 = 0xd;
    }
    else {
      uVar1 = FUN_140001000(pFVar2,pFVar3,pFVar4);
      FreeLibrary(hLibModule);
      FUN_140001380(s_Marker_task_exit___d_140004080,(ulonglong)uVar1,pFVar4,in_R9);
    }
  }
  return uVar1;
}


