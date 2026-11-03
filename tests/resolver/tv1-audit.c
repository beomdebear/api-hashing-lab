/* Diagnostic tool only: NOT a detector and NOT a dataset sample.
   Has plaintext target names on purpose to check correctness independently. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include "../../samples/common/tv1_resolver.h"

int main(void)
{
    const char *names[3] = { "CreateFileW", "WriteFile", "CloseHandle" };
    HMODULE module = LoadLibraryW(L"kernel32.dll");
    unsigned int i;
    int failures = 0;
    if (!module) return 14;
    puts("api,hash,matches,name_equal,address_equal,status");
    for (i = 0; i < 3; ++i) {
        const char *matched = NULL;
        DWORD count = 0;
        FARPROC resolved = NULL;
        uint32_t h = tv1_hash(names[i]);
        int rc = tv1_find_name(module, h, &matched, &count);
        int same_name = rc == 0 && strcmp(matched, names[i]) == 0;
        int same_address;
        if (!rc) rc = tv1_resolve(module, h, &resolved);
        same_address = rc == 0 && resolved == GetProcAddress(module, names[i]);
        printf("%s,0x%08lX,%lu,%d,%d,%d\n", names[i], (unsigned long)h,
               count, same_name, same_address, rc);
        if (rc || !same_name || !same_address) ++failures;
    }
    FreeLibrary(module);
    return failures ? 1 : 0;
}
