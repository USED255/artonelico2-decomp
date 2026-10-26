struct S { char c; char pad[3]; int x; };
extern char D_00C06E78[];
void func_0023fd98(void){ int i; for (i = 0; i < 0x142; i++) { struct S *p = (struct S *)(i * 8 + (int)D_00C06E78); p->c = 0; p->x = 0; } }
