struct S { int a; int b; };
extern char D_00BB8960[];
void func_0018ff18(void){ int i; for (i = 0; i < 0x4B; i++) { struct S *p = (struct S *)(i * 8 + (int)D_00BB8960); p->a = 0; p->b = 0; } }
