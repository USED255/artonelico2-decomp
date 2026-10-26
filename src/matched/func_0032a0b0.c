struct S { char pad[4]; int f4; };
extern char D_009D3758[];
extern void func_0031c878(void *);
extern void func_00324320(int);
void func_0032a0b0(struct S *p){ if (!p) { func_0031c878(D_009D3758); return; } func_00324320(p->f4); }
