struct S { char pad[0x1780]; int f1780; };
extern char D_00BC3400[];
extern void func_0013f8dc(struct S *);
extern void func_001357f4(int);
extern void func_00180588(void);
extern void func_001ce9e8(void *);
void func_00236930(struct S *p){ func_0013f8dc(p); func_001357f4(-1); if (p->f1780 == 1) func_00180588(); func_001ce9e8(D_00BC3400); }
