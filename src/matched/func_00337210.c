struct S { char pad; signed char b; char pad2[0x1A]; int f1C; int f20; int f24; };
extern char D_009D5A58[];
extern void func_00337b50(void *);
void func_00337210(struct S *p){ if (!p) { func_00337b50(D_009D5A58); return; } if (!p->b) { p->f24 = 0; p->f1C = 0; p->f20 = 0; } }
