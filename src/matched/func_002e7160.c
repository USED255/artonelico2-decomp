struct S { char pad[4]; };
extern char D_009D0098[];
extern char D_009D00C8[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *);
extern int func_002e5de0(struct S *);
extern void func_002e5e08(struct S *, int *, void *);
extern void func_00304d98(int, void *);
void func_002e7160(struct S *p, int *o){ char buf[0xA0]; int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009D0098); return; } if (!*o) { func_002e90c8(D_009D00C8); return; } { int x = func_002e5de0(p); func_002e5e08(p, o, buf); func_00304d98(x, buf); } }
