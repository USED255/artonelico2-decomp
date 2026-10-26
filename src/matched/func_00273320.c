struct S { int a; short b; short c; int d; };
void func_00273320(struct S *p){ p->a = 0; p->b = -1; p->c = 0; p->d = p->d & ~1; p->d = p->d & ~2; p->d = p->d & ~4; }
