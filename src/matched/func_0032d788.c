struct S { char pad[0x1C0]; int f; };
extern char D_009D3C88[];
extern void func_00342ef8(void *);
void func_0032d788(struct S *p, int v){ if (!p) { func_00342ef8(D_009D3C88); return; } p->f = v; }
