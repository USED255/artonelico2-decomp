struct S { char pad[0x44]; int f44; };
extern int func_002efef8(struct S *);
extern int func_002efcd8(int, int);
extern int func_002fb370(struct S *);
int func_002fb318(struct S *p){ int r; if (func_002efef8(p)) return func_002efcd8(0, 0xFF000133); r = func_002fb370(p); p->f44 = 1; return r; }
