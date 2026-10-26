struct S { char pad[0x60]; short f; };
extern char D_009D34C8[];
extern void func_0031c878(void *);
int func_00329000(struct S *p){ if (!p) { func_0031c878(D_009D34C8); return -1; } return p->f; }
