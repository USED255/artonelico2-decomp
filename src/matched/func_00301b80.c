struct S { char pad[0x10]; int f10; };
extern int func_00302ba0(struct S *);
extern int func_00303a50(struct S *);
int func_00301b80(struct S *p){ switch (p->f10) { case 0x64: return func_00302ba0(p); case 0xC8: return func_00303a50(p); default: return 0; } }
