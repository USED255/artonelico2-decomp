extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
extern int func_00208bf0(int, int, int, int, int);
extern int func_00208d68(int, int);
extern int func_00208e2c(int);
extern void func_00234510(void *, void *, int);
void func_00207368(int a, int b, int c, int d, int e){ char buf[0x10]; int t, nt; t = func_00208bf0(c, a, b, e, 0); t = t + func_00208d68(b, t); func_0021b834(buf); buf[8] = 0; nt = -t; *(int *)buf = nt; *(short *)(buf + 4) = 0; buf[9] = func_00208e2c(e); func_0021be98((void *)(long)a, (void *)(long)b, buf); func_00234510((void *)(long)a, (void *)(long)b, nt); }
