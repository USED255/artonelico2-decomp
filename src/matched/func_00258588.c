struct S { char pad[0x40]; short a; short b; };
extern void func_00258994(struct S *);
extern void func_002587e4(struct S *);
void func_00258588(struct S *p, int x, int y){ p->a = y; p->b = x; func_00258994(p); func_002587e4(p); }
