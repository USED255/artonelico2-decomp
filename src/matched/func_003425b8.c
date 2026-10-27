void func_003425b8(char *p, char *q){ unsigned char lo, hi; p = p + 2; hi = *(unsigned char *)p; lo = *(unsigned char *)(p + 1); *(short *)(q + 0xE) = lo | (hi << 8); }
