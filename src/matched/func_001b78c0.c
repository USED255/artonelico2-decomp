struct S { char pad[0x12]; short h12; };
extern void func_00125c1c(void *, int, int);
void func_001b78c0(struct S *p, int v){ p->h12 = v; func_00125c1c((char *)p + 0x50, (short)v, 0); }
