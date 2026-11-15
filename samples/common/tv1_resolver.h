#ifndef TV1_RESOLVER_H
#define TV1_RESOLVER_H
#include <windows.h>
#include <stdint.h>
#include <string.h>
#include "tv1_hash.h"

/* Only accepts a valid system DLL already loaded by Windows into THIS process.
   This is not an on-disk PE parser or a parser for arbitrary untrusted bytes. */
static int tv1_span(DWORD rva, SIZE_T bytes, DWORD image_size)
{
    return rva < image_size && bytes <= (SIZE_T)(image_size - rva);
}

/* Scan ALL exported names, so duplicate hashes are rejected, not silently used.
   Return 0 success, 10 absent, 11 collision, 12 invalid module metadata.
   match_count covers this target only; it is not a claim about all possible names. */
static int tv1_find_name(HMODULE module, uint32_t target,
                         const char **matched_name, DWORD *match_count)
{
    const BYTE *base = (const BYTE *)module;
    const IMAGE_DOS_HEADER *dos;
    const IMAGE_NT_HEADERS64 *nt;
    const IMAGE_EXPORT_DIRECTORY *exports;
    IMAGE_DATA_DIRECTORY dir;
    const DWORD *names;
    DWORD image_size, i;
    *matched_name = NULL;
    *match_count = 0;
    if (!module) return 12;
    dos = (const IMAGE_DOS_HEADER *)base;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE || dos->e_lfanew <= 0)
        return 12;
    nt = (const IMAGE_NT_HEADERS64 *)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE ||
        nt->OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR64_MAGIC ||
        nt->OptionalHeader.NumberOfRvaAndSizes <= IMAGE_DIRECTORY_ENTRY_EXPORT)
        return 12;
    image_size = nt->OptionalHeader.SizeOfImage;
    dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
    if (!dir.VirtualAddress || dir.Size < sizeof(IMAGE_EXPORT_DIRECTORY) ||
        !tv1_span(dir.VirtualAddress, dir.Size, image_size)) return 12;
    exports = (const IMAGE_EXPORT_DIRECTORY *)(base + dir.VirtualAddress);
    if (!exports->AddressOfNames ||
        !tv1_span(exports->AddressOfNames,
                  (SIZE_T)exports->NumberOfNames * sizeof(DWORD), image_size))
        return 12;
    names = (const DWORD *)(base + exports->AddressOfNames);
    for (i = 0; i < exports->NumberOfNames; ++i) {
        const char *name;
        if (!tv1_span(names[i], 1, image_size)) return 12;
        name = (const char *)(base + names[i]);
        if (!memchr(name, 0, image_size - names[i])) return 12;
        if (tv1_hash(name) == target) {
            ++*match_count;
            *matched_name = name;
        }
    }
    if (*match_count == 0) return 10;
    if (*match_count != 1) { *matched_name = NULL; return 11; }
    return 0;
}

static int tv1_resolve(HMODULE module, uint32_t target, FARPROC *address)
{
    const char *name;
    DWORD matches;
    int rc;
    *address = NULL;
    rc = tv1_find_name(module, target, &name, &matches);
    if (rc != 0) return rc;
    /* Windows handles forwarded exports; no hand-written forwarder resolver. */
    *address = GetProcAddress(module, name);
    return *address ? 0 : 13;
}
#endif
