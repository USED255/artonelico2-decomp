typedef unsigned long long uint64_t;
extern int func_00244294(int);
int func_002433fc(char *p) {
    int r;
    if (func_00244294(*(short *)(p + 0xD90)) == 0) r = 1;
    else {
        *(volatile short *)p = 8;
        volatile uint64_t *q = (volatile uint64_t *)p;
        uint64_t mask = 1ULL << 32;
        uint64_t val = *q;
        val |= mask;
        *q = val;
        r = -1;
    }
    return r;
}
