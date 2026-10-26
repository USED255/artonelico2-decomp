struct S { char pad[0x10]; int f10; };
extern int func_00303120(struct S *);
extern int func_00303f88(struct S *);
int func_00302160(struct S *p){ switch (p->f10) { case 0x64: return func_00303120(p); case 0xC8: return func_00303f88(p); default: return 0; } }
