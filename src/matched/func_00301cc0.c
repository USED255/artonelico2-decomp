struct S { char pad[0x10]; int f10; };
extern int func_00302e10(struct S *);
extern int func_00303bd8(struct S *);
int func_00301cc0(struct S *p){ switch (p->f10) { case 0x64: return func_00302e10(p); case 0xC8: return func_00303bd8(p); default: return 0; } }
