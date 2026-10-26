struct S { char pad[4]; int f; };
extern int func_0031a3b8(int);
int func_00324568(struct S *p){ if (!p) return 0; return func_0031a3b8(p->f); }
