#include <stdio.h>
#include "../../samples/common/tv1_hash.h"
int main(void) {
    printf("%08lX\n", (unsigned long)tv1_hash(""));
    printf("%08lX\n", (unsigned long)tv1_hash("123456789"));
    printf("%08lX\n", (unsigned long)tv1_hash("CreateFileW"));
    printf("%08lX\n", (unsigned long)tv1_hash("WriteFile"));
    printf("%08lX\n", (unsigned long)tv1_hash("CloseHandle"));
    return 0;
}
