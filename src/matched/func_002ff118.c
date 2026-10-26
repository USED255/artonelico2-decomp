struct T { char pad[0x2E4]; int f2E4; int f2E8; };
struct S { char pad[0xD88]; struct T t; };
extern int func_00312b80(int);
extern void func_002eff98(void *);
extern void func_002effb0(void *);
void func_002ff118(struct S *p){ struct T *t = &p->t; char buf[0x10]; int x = func_00312b80(t->f2E8); func_002eff98(buf); t->f2E4 = t->f2E4 + x; func_002effb0(buf); }
