/* TV2 proposed control for role B4: hashes DATA only.
   DJB2 is applied to the marker text and printed as a checksum. All file APIs are
   ordinary imports; the hash never selects, names or locates an API. */
#include "../tv2_control.h"

static uint32_t data_checksum(const char *text)
{
    uint32_t h = UINT32_C(5381);
    const unsigned char *p = (const unsigned char *)text;
    while (*p != 0) {
        h = h * UINT32_C(33) + (uint32_t)*p++;
    }
    return h;
}

int main(void)
{
    DWORD written = 0;
    BOOL write_ok, close_ok;
    int rc = 0;
    HANDLE file;
    printf("Marker checksum: 0x%08X\n", data_checksum(TV2_MARKER));
    file = CreateFileW(L"marker.txt", GENERIC_WRITE, 0, NULL,
                       CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 30;
    write_ok = WriteFile(file, TV2_MARKER, (DWORD)(sizeof(TV2_MARKER) - 1), &written, NULL);
    close_ok = CloseHandle(file);
    if (!write_ok || written != (DWORD)(sizeof(TV2_MARKER) - 1)) rc = 31;
    else if (!close_ok) rc = 32;
    printf("Marker task exit: %d\n", rc);
    return rc;
}
