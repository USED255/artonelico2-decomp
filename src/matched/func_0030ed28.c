struct S { int f; };
extern struct S *D_00A30D98;
int func_0030ed28(struct S *p){ D_00A30D98 = p; if (!p) return -1; return p->f == 1 ? -1 : 0; }
