typedef unsigned long long uint64_t;
unsigned int D_009DF2A0 __attribute__((section(".sdata"), weak));
extern void func_0023c5d8(void *);
void func_0023d174(void) {
    char *p = (char *)D_009DF2A0;
    if (p) {
        *(volatile short *)p = 15;
    volatile uint64_t *q = (volatile uint64_t *)p;
    uint64_t mask = 1ULL << 32;
    uint64_t val = *q;
    val |= mask;
    *q = val;
        func_0023c5d8(p);
    }
}
