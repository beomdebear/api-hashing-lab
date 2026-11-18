
/* Library Function - Single Match
    _vfprintf_l
   
   Library: Visual Studio 2019 Release */

int __cdecl _vfprintf_l(FILE *_File,char *_Format,_locale_t _Locale,va_list _ArgList)

{
  int iVar1;
  undefined8 *puVar2;
  
  puVar2 = (undefined8 *)FUN_1400011c0();
  iVar1 = __stdio_common_vfprintf(*puVar2,_File,_Format,_Locale,_ArgList);
  return iVar1;
}


