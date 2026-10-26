struct S { char pad[8]; int f8; int fC; int f10; };
extern void func_00342eb8(struct S *);
extern void func_00342ed0(void);
void func_0032f3b0(struct S *p){ func_00342eb8(p); p->f10 = 0; p->f8 = 0; p->fC = 0; ((char *)p)[1] = 1; func_00342ed0(); }
