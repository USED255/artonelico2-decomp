extern volatile int D_0081BB88[];
extern void *func_00312ff0(void);
extern void func_00313040(void *);
void *func_00312f98(void){ char *p = func_00312ff0(); if (p == 0) return p; func_00313040(p); D_0081BB88[0] = D_0081BB88[0] + 1; *(int *)p = 1; return p; }
