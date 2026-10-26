typedef unsigned long long uint64_t;
int func_0023c784(char *p) {
    unsigned short v = *(unsigned short *)(p + 0x19BC);
    if ((short)v <= 0) {
        *(volatile short *)p = 17;
        volatile uint64_t *q = (volatile uint64_t *)p;
        uint64_t mask = 1ULL << 32;
        uint64_t val = *q;
        val |= mask;
        *q = val;
    } else {
        *(unsigned short *)(p + 0x19BC) = v - 1;
    }
    return -1;
}
