typedef signed short s16;
typedef signed int s32;
typedef unsigned char uint8_t;
typedef unsigned long long uint64_t;
int func_002a0294();
s32 func_001a01b8(s16 *arg0) {
    s16 *ptr = arg0;
    s32 ret = func_002a0294(ptr);
    if (ret != -1) {
        return -1;
    }
    *(volatile s16 *)ptr = 1;
    volatile uint64_t *p = (volatile uint64_t *)ptr;
    uint64_t mask = 1ULL;
    mask = mask << 32;
    uint64_t val = *p;
    val |= mask;
    *p = val;
    return -1;
}
