struct S { char pad[1]; signed char b1; char pad2[0x92]; int f94; };
extern char D_009D2CF0[];
extern void func_0031c878(void *);
extern void func_003371e0(int);
void func_00320a48(struct S *p){ if (!p) { func_0031c878(D_009D2CF0); return; } if (p->b1) return; func_003371e0(p->f94); }
