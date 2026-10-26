struct S { char pad[0x72]; signed char f; };
extern char D_009D3650[];
extern void func_0031c878(void *);
int func_00329560(struct S *p){ if (!p) { func_0031c878(D_009D3650); return 0; } return p->f; }
