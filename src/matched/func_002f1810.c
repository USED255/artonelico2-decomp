struct T { char pad[0x14]; int f14; int f18; int f1C; };
struct S { char pad[0x1FE4]; struct T t; };
extern void func_002edb18(struct S *, int, int);
void func_002f1810(struct S *p, int a){ struct T *t = &p->t; if (t->f18 != 8) func_002edb18(p, t->f18, a); if (t->f14 != 8) func_002edb18(p, t->f14, a); if (t->f1C != 8) func_002edb18(p, t->f1C, a); }
