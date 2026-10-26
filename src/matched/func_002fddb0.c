struct S { int f0; char pad[0x20]; int f24; int f28; };
extern void func_002fddf8(void *);
void func_002fddb0(struct S *p, int v){ p->f0 = 0; func_002fddf8((char *)p + 4); p->f24 = v; p->f28 = 1; }
