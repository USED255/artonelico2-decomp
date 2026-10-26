struct S { char pad[0x49]; signed char a; char pad2[3]; signed char b; };
int func_00324ea8(struct S *p){ if (p->a) return 0; return p->b != 0; }
