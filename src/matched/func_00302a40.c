struct S { char pad[4]; int f4; };
extern int func_00302b58(int, int);
int func_00302a40(struct S *p, int x, int *out){ int r; *out = 0; r = func_00302b58(p->f4, x & 0xFF); if (r) *out = 1; else *out = 0; return *out; }
