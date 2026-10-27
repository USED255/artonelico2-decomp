extern char D_009D0F80[];
extern char *LibcString_23(char *, void *);
extern int func_00303dc0(void *, int);
int func_00303d60(char *p, int a, int b){ char *q = LibcString_23(p, D_009D0F80); int r; if (q == 0) return 0; r = func_00303dc0(q + 4, a); func_00303dc0((char *)r + 1, b); return 1; }
