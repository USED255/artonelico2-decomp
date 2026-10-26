struct S { char a; char b; char pad[2]; int c; };
extern char D_00C07888[];
void func_0024501c(void){ int i; for (i = 0; i < 0xF3; i++) { struct S *p = (struct S *)(i * 8 + (int)D_00C07888); p->b = 0; p->a = 0; p->c = -1; } }
