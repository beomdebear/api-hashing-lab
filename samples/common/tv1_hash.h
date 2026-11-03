#ifndef TV1_HASH_H
#define TV1_HASH_H
#include <stdint.h>
/* Select one algorithm at compile time; do not link unused hash algorithms. */
#ifndef TV1_ALGORITHM
#define TV1_ALGORITHM 1
#endif
#ifndef TV1_SEED
#if TV1_ALGORITHM == 1
#define TV1_SEED UINT32_C(5381)
#elif TV1_ALGORITHM == 2
#define TV1_SEED UINT32_C(2166136261)
#else
#define TV1_SEED UINT32_C(0xFFFFFFFF)
#endif
#endif
static uint32_t tv1_hash(const char *text)
{
    uint32_t h = TV1_SEED;
    const unsigned char *p = (const unsigned char *)text;
    while (*p != 0) {
#if TV1_ALGORITHM == 1
        h = h * UINT32_C(33) + (uint32_t)*p++;
#elif TV1_ALGORITHM == 2
        h ^= (uint32_t)*p++;
        h *= UINT32_C(16777619);
#elif TV1_ALGORITHM == 3
        unsigned int bit;
        h ^= (uint32_t)*p++;
        for (bit = 0; bit < 8; ++bit) {
            h = (h >> 1) ^ ((h & 1) ? UINT32_C(0xEDB88320) : 0);
        }
#else
#error Unsupported TV1_ALGORITHM
#endif
    }
#if TV1_ALGORITHM == 3
    return h ^ UINT32_C(0xFFFFFFFF);
#else
    return h;
#endif
}
#endif
