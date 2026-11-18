
undefined4 FUN_140001000(undefined *param_1,undefined *param_2,undefined *param_3)

{
  int iVar1;
  int local_28;
  undefined4 local_24;
  int local_20;
  longlong local_18;
  
  local_28 = 0;
  local_18 = (*(code *)param_1)(u_marker_txt_140004030,0x40000000,0,0,1,0x80,0);
  if (local_18 == -1) {
    local_24 = 0x1e;
  }
  else {
    local_20 = (*(code *)param_2)(local_18,s_D08_LAB_MARKER_140004048,0x10,&local_28,0);
    iVar1 = (*(code *)param_3)(local_18);
    if ((local_20 == 0) || (local_28 != 0x10)) {
      local_24 = 0x1f;
    }
    else if (iVar1 == 0) {
      local_24 = 0x20;
    }
    else {
      local_24 = 0;
    }
  }
  return local_24;
}


