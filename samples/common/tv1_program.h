#ifndef TV1_PROGRAM_H
#define TV1_PROGRAM_H
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <string.h>

/* This file only creates ./marker.txt in the working directory.
   CREATE_NEW refuses to overwrite an existing file. The run script gives each
   execution its own directory below artifacts/runs/tv1/. */
#define TV1_MARKER "D08 LAB MARKER\r\n"

#if TV1_MODE != 0
typedef HANDLE (WINAPI *TV1_CREATE)(LPCWSTR, DWORD, DWORD,
    LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
typedef BOOL (WINAPI *TV1_WRITE)(HANDLE, LPCVOID, DWORD, LPDWORD, LPOVERLAPPED);
typedef BOOL (WINAPI *TV1_CLOSE)(HANDLE);
#endif
#if TV1_MODE == 2
#include "tv1_resolver.h"
#endif

int main(int argc, char **argv)
{
    HANDLE file;
    DWORD written = 0;
    BOOL write_ok, close_ok;
    int rc = 0;
#if TV1_MODE != 0
    HMODULE module;
    TV1_CREATE create_file;
    TV1_WRITE write_file;
    TV1_CLOSE close_handle;
#endif
#if TV1_MODE == 2
    FARPROC addresses[3] = { NULL, NULL, NULL };
    const uint32_t targets[3] = { TV1_TARGET_CREATE, TV1_TARGET_WRITE, TV1_TARGET_CLOSE };
#ifdef TV1_REVERSE_ORDER
    const unsigned int order[3] = { 1, 2, 0 };
#else
    const unsigned int order[3] = { 0, 1, 2 };
#endif
    unsigned int i;
#endif
    (void)argc;
    (void)argv;
#ifdef TV1_EARLY_EXIT
    /* Runtime condition retains a reachable hashing path. Default E2 stops.
       --continue is for manual correctness checks only, not the E2 test run. */
    if (argc != 2 || strcmp(argv[1], "--continue") != 0) {
        puts("Stopped before target behavior.");
        return 20;
    }
#endif
#if TV1_MODE != 0
    module = LoadLibraryW(L"kernel32.dll");
    if (!module) { printf("Load failed: %lu\n", GetLastError()); return 14; }
#if TV1_MODE == 1
    create_file = (TV1_CREATE)GetProcAddress(module, "CreateFileW");
    write_file = (TV1_WRITE)GetProcAddress(module, "WriteFile");
    close_handle = (TV1_CLOSE)GetProcAddress(module, "CloseHandle");
    if (!create_file || !write_file || !close_handle) {
        FreeLibrary(module); puts("Resolve failed."); return 13;
    }
#else
#ifdef TV1_WRONG_HASH
    rc = tv1_resolve(module, TV1_TARGET_CREATE ^ UINT32_C(0x80000000), &addresses[0]);
    FreeLibrary(module);
    if (rc == 10) { puts("Wrong hash not found."); return 10; }
    /* A wrong hash could accidentally match on another Windows version.
       NEVER call that pointer; report an unexpected fixture outcome. */
    printf("Unexpected wrong-hash outcome: %d\n", rc);
    return 21;
#else
    for (i = 0; i < 3; ++i) {
        unsigned int slot = order[i];
        rc = tv1_resolve(module, targets[slot], &addresses[slot]);
        if (rc) {
            printf("Resolve slot %u failed: %d\n", slot, rc);
            FreeLibrary(module); return rc;
        }
    }
    create_file = (TV1_CREATE)addresses[0];
    write_file = (TV1_WRITE)addresses[1];
    close_handle = (TV1_CLOSE)addresses[2];
#endif
#endif
#endif

#if TV1_MODE == 0
    file = CreateFileW(L"marker.txt", GENERIC_WRITE, 0, NULL,
                       CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
#else
    file = create_file(L"marker.txt", GENERIC_WRITE, 0, NULL,
                       CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
#endif
    if (file == INVALID_HANDLE_VALUE) {
        printf("Create failed: %lu\n", GetLastError()); rc = 30;
    } else {
#if TV1_MODE == 0
        write_ok = WriteFile(file, TV1_MARKER, (DWORD)(sizeof(TV1_MARKER) - 1), &written, NULL);
        close_ok = CloseHandle(file);
#else
        write_ok = write_file(file, TV1_MARKER, (DWORD)(sizeof(TV1_MARKER) - 1), &written, NULL);
        close_ok = close_handle(file);
#endif
        if (!write_ok || written != (DWORD)(sizeof(TV1_MARKER) - 1)) rc = 31;
        else if (!close_ok) rc = 32;
    }
#if TV1_MODE != 0
    FreeLibrary(module);
#endif
    printf("Marker task exit: %d\n", rc);
    return rc;
}
#endif
