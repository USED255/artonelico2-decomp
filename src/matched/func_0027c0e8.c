struct S { char pad[0x902]; unsigned short a; };
extern void func_0027bf4c(struct S *, int);
void func_0027c0e8(struct S *p, int v){ p->a = (p->a & 0x3FFF) | ((v & 0xFF) << 14); func_0027bf4c(p, v); }
