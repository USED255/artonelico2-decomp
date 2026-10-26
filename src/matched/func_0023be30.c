typedef unsigned long long uint64_t;
extern int func_00140034(void *);
int func_0023be30(char *p) {
    int r = func_00140034(p);
    if (r != 2) return -1;
    *(volatile short *)p = 11;
    volatile uint64_t *q = (volatile uint64_t *)p;
    uint64_t mask = 1ULL << 32;
    uint64_t val = *q;
    val |= mask;
    *q = val;
    return -1;
}
