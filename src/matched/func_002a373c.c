struct S { char pad[0x5A0]; int f5A0; };
extern void func_002a3514(struct S *, int);
extern void func_002a35c4(struct S *, int);
void func_002a373c(struct S *p, int mode, int x){ p->f5A0 = mode; switch (mode) { case 0: func_002a3514(p, x); break; case 1: func_002a35c4(p, x); break; } }
