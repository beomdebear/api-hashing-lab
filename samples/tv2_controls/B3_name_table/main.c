/* TV2 proposed control for role B3: valid resolve by plain name.
   API names are ordinary strings in a table; no hash is computed anywhere. */
#include "../tv2_control.h"

static const char *const kApiNames[3] = { "CreateFileW", "WriteFile", "CloseHandle" };

int main(void)
{
    FARPROC resolved[3] = { NULL, NULL, NULL };
    unsigned int i;
    int rc;
    HMODULE module = GetModuleHandleW(L"kernel32.dll");
    if (!module) return 14;
    for (i = 0; i < 3; ++i) {
        resolved[i] = GetProcAddress(module, kApiNames[i]);
        if (!resolved[i]) return 13;
    }
    rc = tv2_marker_task((TV2_CREATE)resolved[0], (TV2_WRITE)resolved[1],
                         (TV2_CLOSE)resolved[2]);
    printf("Marker task exit: %d\n", rc);
    return rc;
}
