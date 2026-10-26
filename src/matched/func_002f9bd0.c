struct S { char pad[4]; };
extern int func_002efef8(struct S *);
extern int func_002efcd8(int, int);
extern void func_002f9c80(struct S *);
int func_002f9bd0(struct S *p){ if (func_002efef8(p)) return func_002efcd8(0, 0xFF000138); func_002f9c80(p); return 0; }
