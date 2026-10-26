typedef unsigned long long uint64_t;
extern void func_0023f9d8(void);
extern void func_0023f8ac(void *);
int func_0023b7b0(char *p) {
    if (*(short *)(p + 0x1338) == 4) {
        func_0023f9d8();
        func_0023f8ac(p);
    }
    *(volatile short *)p = 5;
    volatile uint64_t *q = (volatile uint64_t *)p;
    uint64_t mask = 1ULL << 32;
    uint64_t val = *q;
    val |= mask;
    *q = val;
    return -1;
}
