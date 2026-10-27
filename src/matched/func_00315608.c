extern int LibcString_6(void *, int, int);
int func_00315608(char *p, int b, int c){ char *q = p + 0x16C; int off = *(int *)(q + 8); int base = *(int *)q; int len = *(int *)(q + 4) - off; int n = (c < len) ? c : len; *(int *)(q + 8) = off + n; return LibcString_6((char *)(base + off), b, n); }
