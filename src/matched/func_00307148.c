extern int func_00307080(char *, int);
extern char D_009D1588[];
extern int LibcString_18(void *, void *, int);
int func_00307148(char *p, int n){ if (p == 0 || n < 0) return 0; if (func_00307080(p, n) == 0) return 0; return (unsigned int)LibcString_18(p + 0x14, D_009D1588, 1) < 1; }
