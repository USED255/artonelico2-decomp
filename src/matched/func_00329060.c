struct S { char pad[0x60]; short a; int b; short c; short d; };
extern char D_009D34F8[];
extern void func_0031c878(void *);
void func_00329060(struct S *p){ if (!p) { func_0031c878(D_009D34F8); return; } p->a = 0; p->b = 0; p->c = 0; p->d = 0; }
