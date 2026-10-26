struct S { char pad[0x10]; int f10; };
extern int func_003030b0(struct S *);
extern int func_00303ea8(struct S *);
int func_00302020(struct S *p){ switch (p->f10) { case 0x64: return func_003030b0(p); case 0xC8: return func_00303ea8(p); default: return 0; } }
