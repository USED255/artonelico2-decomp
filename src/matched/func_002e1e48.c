struct S { char pad[0x48]; int f; };
extern void func_002E1E70(void);
extern void func_002fd728(int, void *, struct S *);
void func_002e1e48(struct S *p){ func_002fd728(p->f, (void *)func_002E1E70, p); }
