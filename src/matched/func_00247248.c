struct S { char a; char b; char pad[2]; int c; };
extern char D_00C08020[];
void func_00247248(void){ int i; for (i = 0; i < 0x51; i++) { struct S *p = (struct S *)(i * 8 + (int)D_00C08020); p->b = 0; p->a = 0; p->c = -1; } }
