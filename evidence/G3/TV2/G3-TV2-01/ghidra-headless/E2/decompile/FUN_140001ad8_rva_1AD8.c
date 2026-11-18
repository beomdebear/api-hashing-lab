
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_140001ad8(void)

{
  code *pcVar1;
  BOOL BVar2;
  undefined1 *puVar3;
  undefined1 auStack_38 [8];
  undefined1 auStack_30 [48];
  
  BVar2 = IsProcessorFeaturePresent(0x17);
  puVar3 = auStack_38;
  if (BVar2 != 0) {
    pcVar1 = (code *)swi(0x29);
    (*pcVar1)(2);
    puVar3 = auStack_30;
  }
  *(undefined8 *)(puVar3 + -8) = 0x140001b03;
  FUN_140001bac((PCONTEXT)&DAT_140004220);
  _DAT_140004190 = *(undefined8 *)(puVar3 + 0x38);
  _DAT_1400042b8 = puVar3 + 0x40;
  _DAT_1400042a0 = *(undefined8 *)(puVar3 + 0x40);
  _DAT_140004180 = 0xc0000409;
  _DAT_140004184 = 1;
  _DAT_140004198 = 1;
  DAT_1400041a0 = 2;
  *(undefined8 *)(puVar3 + 0x20) = DAT_140004100;
  *(undefined8 *)(puVar3 + 0x28) = DAT_140004140;
  *(undefined8 *)(puVar3 + -8) = 0x140001ba5;
  DAT_140004318 = _DAT_140004190;
  __raise_securityfailure((_EXCEPTION_POINTERS *)&PTR_DAT_140003270);
  return;
}


