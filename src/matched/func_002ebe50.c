struct S { char pad[4]; };
extern void func_002ff168(struct S *, int *, int *);
extern int func_00312b80(int, int, int);
void func_002ebe50(struct S *p, int *out, int q){ int a, b; func_002ff168(p, &a, &b); *out = func_00312b80(q, a, b); }
