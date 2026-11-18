
int FUN_140001000(byte *param_1)

{
  int local_18;
  byte *local_10;
  
  local_18 = 0x539;
  for (local_10 = param_1; *local_10 != 0; local_10 = local_10 + 1) {
    local_18 = local_18 * 0x21 + (uint)*local_10;
  }
  return local_18;
}


