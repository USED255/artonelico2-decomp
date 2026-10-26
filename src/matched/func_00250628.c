struct S { char pad[0x30]; short h30; short h32; };
extern char D_003D1D68[];
extern void func_0011f03c(void *, void *, int, int);
void func_00250628(struct S *p, int a, int b){ p->h30 = a; p->h32 = b; func_0011f03c(p, D_003D1D68, (short)a, (short)b); }
