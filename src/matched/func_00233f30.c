extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
extern int func_00208a44(int, int, int, int *, int);
extern int func_00208e2c(int *);
void func_00233f30(int a, int b, int c, int d){ int local[4]; char buf[0x10]; int t; *(int *)local = d; local[1] = -1; t = func_00208a44(c, a, b, local, 0); func_0021b834(buf); buf[8] = 0; *(int *)buf = -t; buf[9] = func_00208e2c(local); func_0021be98((void *)(long)a, (void *)(long)b, buf); }
