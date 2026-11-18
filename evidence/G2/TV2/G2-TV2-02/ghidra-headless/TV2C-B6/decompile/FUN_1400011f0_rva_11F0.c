
FARPROC FUN_1400011f0(HMODULE param_1,char *param_2)

{
  char *lpProcName;
  FARPROC local_10;
  
  lpProcName = FUN_1400010e0((short *)param_1,param_2);
  if (lpProcName == (char *)0x0) {
    local_10 = (FARPROC)0x0;
  }
  else {
    local_10 = GetProcAddress(param_1,lpProcName);
  }
  return local_10;
}


