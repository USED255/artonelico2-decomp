struct S { char pad[0x48]; int f48; };
extern char D_009CFBD0[];
extern int func_002e4b58(struct S *);
extern void func_002e90c8(void *, int, int);
extern void func_002fd390(int);
void func_002e5cf0(struct S *p, int b){ int r = func_002e4b58(p); if (r != 1) { func_002e90c8(D_009CFBD0, 0x47, b); return; } func_002fd390(p->f48); }
