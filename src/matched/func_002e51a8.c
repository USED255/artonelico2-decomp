struct S { char pad[4]; };
extern char D_009CF8F8[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *);
extern void func_002e49d0(struct S *, void *);
int func_002e51a8(struct S *p){ char buf[0xB0]; int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009CF8F8); return 0; } func_002e49d0(p, buf); return *(int *)buf; }
