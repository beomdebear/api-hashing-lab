
uint FUN_1400010e0(byte *param_1)

{
  uint local_18;
  byte *local_10;
  
  local_18 = 0x811c9dc5;
  for (local_10 = param_1; *local_10 != 0; local_10 = local_10 + 1) {
    local_18 = (local_18 ^ *local_10) * 0x1000193;
  }
  return local_18;
}


