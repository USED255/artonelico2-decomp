struct S { char pad[4]; };
extern char D_009CFA80[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *);
extern int func_002e4578(struct S *);
extern void func_002fd390(int, int, int);
void func_002e56a8(struct S *p, int a){ int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009CFA80); return; } { int x = func_002e4578(p); func_002fd390(x, 7, (a ^ r) != 0); } }
