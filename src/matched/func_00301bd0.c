struct S { char pad[0x10]; int f10; };
extern int func_00302c08(struct S *);
extern int func_00303a78(struct S *);
int func_00301bd0(struct S *p){ switch (p->f10) { case 0x64: return func_00302c08(p); case 0xC8: return func_00303a78(p); default: return 0; } }
