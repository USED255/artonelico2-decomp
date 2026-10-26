struct S { char pad[0x1924]; signed char b; };
extern void func_00126138(void *);
void func_0023e1f0(int a, struct S *p){ if (p->b) func_00126138((char *)p + 0x19C0); }
