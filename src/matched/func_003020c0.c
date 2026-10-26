struct S { char pad[0x10]; int f10; };
extern int func_003030f0(struct S *);
extern int func_00303f18(struct S *);
int func_003020c0(struct S *p){ switch (p->f10) { case 0x64: return func_003030f0(p); case 0xC8: return func_00303f18(p); default: return 0; } }
