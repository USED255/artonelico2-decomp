extern int D_007AF2D0;
int func_001e41b8(int i){ int b = D_007AF2D0; int t = i / 8; unsigned char *p = (unsigned char *)(t + b + 0xC1CA0); return (p[0xF] >> (i % 8)) & 1; }
