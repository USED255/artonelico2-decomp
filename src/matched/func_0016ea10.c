struct S { char pad[0x10]; int f10; int f14; int pad2[1]; int f1C; };
extern char D_00922A40[];
extern void LibcStdio_46(int, void *, int, int, int);
void func_0016ea10(int x, struct S *p){ LibcStdio_46(x, D_00922A40, p->f10, p->f14, p->f1C); }
