extern char D_009D0F30[];
extern char *LibcString_23(char *, void *);
extern int func_00302fc8(void *, int);
int func_00302f68(char *p, int a, int b){ char *q = LibcString_23(p, D_009D0F30); int r; if (q == 0) return 0; r = func_00302fc8(q + 4, a); func_00302fc8((char *)r + 1, b); return 1; }
