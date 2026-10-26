struct S { char pad[0x6B]; unsigned char b; char pad2[4]; short s; char pad3[0x70]; };
extern void func_001286a0(int, struct S *, int, int, int, int, int);
void func_00127844(int x, struct S *p, int a2, int a3, unsigned char a4, unsigned char a5, unsigned char a6){ if (!p->b) return; if (p->s < 0) return; func_001286a0(x, p, a2, a3, a4, a5, a6); }
