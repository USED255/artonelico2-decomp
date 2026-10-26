extern int D_008291DC;
struct S { char pad[0x38]; int f; };
extern char D_009D3310[];
extern void func_0031c878(void *);
void func_00328730(struct S *p, int v){ if (!p) { func_0031c878(D_009D3310); return; } p->f = v; D_008291DC = v; }
