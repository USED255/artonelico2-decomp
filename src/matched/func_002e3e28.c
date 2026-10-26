struct S { char pad[4]; };
extern char D_009CF430[];
extern char D_009CF468[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *);
extern int func_002e5728(struct S *);
extern void func_002e3760(struct S *, int);
extern void func_002E3D10(struct S *, int, int, int);
void func_002e3e28(struct S *p, int a, int b, int c){ int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009CF430); return; } if (!a) { func_002e90c8(D_009CF468); return; } { int x = func_002e5728(p); func_002e3760(p, x); func_002E3D10(p, a, b, c); } }
