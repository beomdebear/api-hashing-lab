/* TV2 proposed control for role B6: valid resolve by name after walking the
   export names of the loaded kernel32.dll. Names are compared with strcmp against
   plain strings, so the export -> compare -> resolve path exists WITHOUT any hash. */
#include "../tv2_control.h"

static const char *find_export_name(HMODULE module, const char *wanted)
{
    const BYTE *base = (const BYTE *)module;
    const IMAGE_DOS_HEADER *dos = (const IMAGE_DOS_HEADER *)base;
    const IMAGE_NT_HEADERS64 *nt;
    const IMAGE_EXPORT_DIRECTORY *exports;
    const DWORD *names;
    DWORD i;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return NULL;
    nt = (const IMAGE_NT_HEADERS64 *)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return NULL;
    exports = (const IMAGE_EXPORT_DIRECTORY *)(base +
        nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);
    names = (const DWORD *)(base + exports->AddressOfNames);
    for (i = 0; i < exports->NumberOfNames; ++i) {
        const char *name = (const char *)(base + names[i]);
        if (strcmp(name, wanted) == 0) return name;
    }
    return NULL;
}

static FARPROC resolve_by_name(HMODULE module, const char *wanted)
{
    const char *name = find_export_name(module, wanted);
    return name ? GetProcAddress(module, name) : NULL;
}

int main(void)
{
    HMODULE module = LoadLibraryW(L"kernel32.dll");
    TV2_CREATE create_file;
    TV2_WRITE write_file;
    TV2_CLOSE close_handle;
    int rc;
    if (!module) return 14;
    create_file = (TV2_CREATE)resolve_by_name(module, "CreateFileW");
    write_file = (TV2_WRITE)resolve_by_name(module, "WriteFile");
    close_handle = (TV2_CLOSE)resolve_by_name(module, "CloseHandle");
    if (!create_file || !write_file || !close_handle) {
        FreeLibrary(module);
        return 13;
    }
    rc = tv2_marker_task(create_file, write_file, close_handle);
    FreeLibrary(module);
    printf("Marker task exit: %d\n", rc);
    return rc;
}
