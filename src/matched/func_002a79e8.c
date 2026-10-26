struct S { int a, b, f8, fC, f10, f14, f18, f1C, f20; };
void func_002a79e8(struct S *p){ int a = p->a; int b = p->b; p->f20 = 0; p->f8 = a; p->fC = (unsigned)(b - a) >> 4; p->f10 = 0; p->f1C = 0; p->f18 = 0; p->f14 = 0; }
