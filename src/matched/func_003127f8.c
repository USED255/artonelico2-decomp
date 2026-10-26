struct S { char pad[0x1D0]; int a; int b; int c; };
extern void func_00312900(struct S *, int, int, int);
void func_003127f8(struct S *p, int x, int y, int z){ p->b = y; p->a = x; p->c = z; func_00312900(p, x, y, z); }
