struct S { char pad[4]; int f4; };
extern char D_009D3728[];
extern void func_0031c878(void *);
extern void func_003242e8(int);
void func_00329cb0(struct S *p){ if (!p) { func_0031c878(D_009D3728); return; } func_003242e8(p->f4); }
