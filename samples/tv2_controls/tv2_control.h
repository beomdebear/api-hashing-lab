#ifndef TV2_CONTROL_H
#define TV2_CONTROL_H
/* Negative controls PROPOSED by TV2 for the B3-B6 roles (not yet accepted by TV4).
   Each control only creates ./marker.txt in the working directory. CREATE_NEW
   refuses to overwrite an existing file. None of them uses a hash to find an API. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#define TV2_MARKER "D08 LAB MARKER\r\n"

typedef HANDLE (WINAPI *TV2_CREATE)(LPCWSTR, DWORD, DWORD,
    LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
typedef BOOL (WINAPI *TV2_WRITE)(HANDLE, LPCVOID, DWORD, LPDWORD, LPOVERLAPPED);
typedef BOOL (WINAPI *TV2_CLOSE)(HANDLE);

/* Shared marker task for controls that call through resolved pointers. */
static int tv2_marker_task(TV2_CREATE create_file, TV2_WRITE write_file,
                           TV2_CLOSE close_handle)
{
    DWORD written = 0;
    BOOL write_ok, close_ok;
    HANDLE file = create_file(L"marker.txt", GENERIC_WRITE, 0, NULL,
                              CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 30;
    write_ok = write_file(file, TV2_MARKER, (DWORD)(sizeof(TV2_MARKER) - 1),
                          &written, NULL);
    close_ok = close_handle(file);
    if (!write_ok || written != (DWORD)(sizeof(TV2_MARKER) - 1)) return 31;
    return close_ok ? 0 : 32;
}
#endif
