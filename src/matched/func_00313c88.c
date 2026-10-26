struct S { int f; };
extern struct S *D_00A34AB0;
int func_00313c88(struct S *p){ D_00A34AB0 = p; if (!p) return -1; return p->f == 2 ? 0 : -1; }
