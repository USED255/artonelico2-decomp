struct S { char pad[0xDA0]; int fDA0; };
extern int func_002efef8(struct S *);
extern int func_002efcd8(int, int);
int func_002fe918(struct S *p, int a){ if (func_002efef8(p)) return func_002efcd8(0, 0xFF000124); p->fDA0 = a; return 0; }
