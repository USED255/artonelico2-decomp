struct S { char pad[0x4C]; int f; };
extern void func_002ea298(int);
extern void func_002e7e28(struct S *, int);
void func_002e4a98(struct S *p, int v){ func_002ea298(p->f); func_002e7e28(p, v); }
