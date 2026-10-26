struct S { char pad[0x10]; int f10; };
extern int func_003030d8(struct S *);
extern int func_00303ee0(struct S *);
int func_00302070(struct S *p){ switch (p->f10) { case 0x64: return func_003030d8(p); case 0xC8: return func_00303ee0(p); default: return 0; } }
