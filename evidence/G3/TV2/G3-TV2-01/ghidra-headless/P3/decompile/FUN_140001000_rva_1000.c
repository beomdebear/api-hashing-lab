
uint FUN_140001000(byte *param_1)

{
  uint local_28;
  uint local_24;
  uint local_20;
  byte *local_18;
  
  local_28 = 0xffffffff;
  local_18 = param_1;
  while (*local_18 != 0) {
    local_28 = local_28 ^ *local_18;
    local_18 = local_18 + 1;
    for (local_24 = 0; local_24 < 8; local_24 = local_24 + 1) {
      if ((local_28 & 1) == 0) {
        local_20 = 0;
      }
      else {
        local_20 = 0xedb88320;
      }
      local_28 = local_28 >> 1 ^ local_20;
    }
  }
  return local_28 ^ 0xffffffff;
}


