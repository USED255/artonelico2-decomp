struct S { char pad[0x10]; int f10; };
extern int func_00303148(struct S *);
extern int func_00303fc0(struct S *);
int func_003021b0(struct S *p){ switch (p->f10) { case 0x64: return func_00303148(p); case 0xC8: return func_00303fc0(p); default: return 0; } }
