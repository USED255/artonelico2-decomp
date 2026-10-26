typedef signed short s16;
typedef signed int s32;
typedef unsigned int uint32_t;
typedef unsigned char uint8_t;
typedef unsigned long long uint64_t;
int func_002a3780();
s32 func_002a2a70(s16 *arg0) {
    s16 *ptr = arg0;
    s32 ret = func_002a3780((s16 *)((uint8_t *)ptr + 0x138C));
    if (ret != 0) {
        return -1;
    }
    *(volatile s16 *)ptr = 4;
    volatile uint64_t *p = (volatile uint64_t *)ptr;
    uint64_t mask = 1ULL;
    mask = mask << 32;
    uint64_t val = *p;
    val |= mask;
    *p = val;
    return -1;
}
