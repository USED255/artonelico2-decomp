struct S { char pad[0xE7C]; short f7C; char pad2[2]; short fE80; short fE82; };
extern void func_00273e98(struct S *);
extern void func_00274458(struct S *);
int func_00274560(struct S *p, int a, int b){ p->fE80 = a; p->fE82 = b; func_00273e98(p); func_00274458(p); return p->f7C; }
