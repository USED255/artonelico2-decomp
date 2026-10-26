struct S { char pad[0x3720]; int f3720; };
extern int func_002efef8(struct S *);
extern int func_002efcd8(int, int);
int func_002fc700(struct S *p, int a){ if (func_002efef8(p)) return func_002efcd8(0, 0xFF000151); p->f3720 = a; return 0; }
