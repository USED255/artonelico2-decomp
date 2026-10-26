struct S { char pad[0x46]; short f; };
extern char D_009D3280[];
extern void func_0031c878(void *);
int func_00328348(struct S *p){ if (!p) { func_0031c878(D_009D3280); return 0; } return p->f; }
