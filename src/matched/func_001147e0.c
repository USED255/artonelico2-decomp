struct S { char pad[0xC]; char pad2[2]; unsigned short f; };
extern void func_00113c30(int,int,int,int,int,int);
void func_001147e0(int a0, struct S *p, int v, int a3, int a4, int a5, int a6){ p->f += v; func_00113c30(a0, p, a3, a4, a5, a6); p->f -= v; }
