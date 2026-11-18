/* TV2 proposed control for role B5: a hash, a comparison, GetProcAddress and
   indirect calls all coexist, but they are NOT related. FNV-1a only checks the
   integrity of a configuration string; APIs are resolved from plain names.
   0xB5941732 is the FNV-1a value of kConfig, not the hash of any API name. */
#include "../tv2_control.h"

static const char kConfig[] = "mode=marker;version=1";

static uint32_t config_checksum(const char *text)
{
    uint32_t h = UINT32_C(2166136261);
    const unsigned char *p = (const unsigned char *)text;
    while (*p != 0) {
        h ^= (uint32_t)*p++;
        h *= UINT32_C(16777619);
    }
    return h;
}

int main(void)
{
    HMODULE module;
    TV2_CREATE create_file;
    TV2_WRITE write_file;
    TV2_CLOSE close_handle;
    int rc;
    if (config_checksum(kConfig) != UINT32_C(0xB5941732)) {
        puts("Config integrity check failed.");
        return 40;
    }
    module = LoadLibraryW(L"kernel32.dll");
    if (!module) return 14;
    create_file = (TV2_CREATE)GetProcAddress(module, "CreateFileW");
    write_file = (TV2_WRITE)GetProcAddress(module, "WriteFile");
    close_handle = (TV2_CLOSE)GetProcAddress(module, "CloseHandle");
    if (!create_file || !write_file || !close_handle) {
        FreeLibrary(module);
        return 13;
    }
    rc = tv2_marker_task(create_file, write_file, close_handle);
    FreeLibrary(module);
    printf("Marker task exit: %d\n", rc);
    return rc;
}
