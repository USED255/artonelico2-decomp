struct S { char pad[0x48]; int f48; int f4C; };
extern void func_00300300(struct S *, int);
void func_002fb238(struct S *p){ p->f48 = 0; p->f4C = 0; func_00300300(p, 4); }
