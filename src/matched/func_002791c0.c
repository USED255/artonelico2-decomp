struct S { char pad[0x100]; int f; };
extern void func_002791f0(struct S *, int);
void func_002791c0(struct S *p, int v){ p->f = (p->f & ~0x20) | ((v & 1) << 5); func_002791f0(p, v); }
