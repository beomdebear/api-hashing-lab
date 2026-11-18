
int FUN_140001680(char *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  int iVar1;
  FILE *_File;
  undefined8 local_res10;
  undefined8 local_res18;
  undefined8 local_res20;
  
  local_res10 = param_2;
  local_res18 = param_3;
  local_res20 = param_4;
  _File = (FILE *)__acrt_iob_func(1);
  iVar1 = _vfprintf_l(_File,param_1,(_locale_t)0x0,(va_list)&local_res10);
  return iVar1;
}


