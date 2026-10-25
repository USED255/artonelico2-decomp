struct S { int f; };
extern struct S *D_00A30E1C;
int func_00312820(struct S *p){ D_00A30E1C = p; if (!p) return -1; return *(int *)((char *)p + 0x188) == 2 ? 0 : -1; }
