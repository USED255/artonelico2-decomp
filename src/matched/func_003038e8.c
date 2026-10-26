struct S { char pad[4]; int f4; };
extern int func_003039b0(int, int);
int func_003038e8(struct S *p, int x, int *out){ int r; *out = 0; r = func_003039b0(p->f4, x & 0xFF); if (r) *out = 1; else *out = 0; return *out; }
