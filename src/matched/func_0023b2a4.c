typedef unsigned long long uint64_t;
extern void func_0019e7d0(int, int);
extern void func_0023f8ac(void *);
extern char D_009DFD0C;
int func_0023b2a4(char *p) {
    func_0019e7d0(*(short *)(p + 0x1338), 1);
    if (D_009DFD0C != 0) return 1;
    func_0023f8ac(p);
    *(volatile short *)p = 4;
    volatile uint64_t *q = (volatile uint64_t *)p;
    uint64_t mask = 1ULL << 32;
    uint64_t val = *q;
    val |= mask;
    *q = val;
    return -1;
}
