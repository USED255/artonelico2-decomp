struct S { char pad[0x40]; short f; };
extern char D_009D32E0[];
extern void func_0031c878(void *);
int func_00328460(struct S *p){ if (!p) { func_0031c878(D_009D32E0); return 0; } return p->f; }
