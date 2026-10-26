struct S { char pad[4]; int f; };
extern char D_009D25C8[];
extern void func_0031c878(void *);
extern int func_00324ea8(int);
int func_0031e0c0(struct S *p){ if (!p) { func_0031c878(D_009D25C8); return 0; } return func_00324ea8(p->f); }
