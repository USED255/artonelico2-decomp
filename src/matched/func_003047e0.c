struct S { char pad[0x44]; int a; int b; };
extern void func_00305e40(struct S *, int, int);
void func_003047e0(int u, struct S *p, int x, int y, int z, int w){ p->a = z; p->b = w; func_00305e40(p, x, y); }
