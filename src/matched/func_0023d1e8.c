typedef unsigned long long uint64_t;
unsigned int D_009DF2A0 __attribute__((section(".sdata"), weak));
extern void func_0023c8d8(void *);
void func_0023d1e8(int v) {
    char *p = (char *)D_009DF2A0;
    if (p) {
        *(short *)(p + 0x1344) = v;
        *(volatile short *)p = 18;
    volatile uint64_t *q = (volatile uint64_t *)p;
    uint64_t mask = 1ULL << 32;
    uint64_t val = *q;
    val |= mask;
    *q = val;
        func_0023c8d8(p);
    }
}
