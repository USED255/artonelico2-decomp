extern int eekernel_70(void *);
extern int func_001064e0(void *, void *, int, int, int);
extern void func_00106408(void *);
extern void func_002b6a50(void *);
extern void func_00106488(void);
extern void func_00106540(void);
extern void func_001062e4(void);
extern char D_009E2790[];
int D_009DB7AC __attribute__((section(".sdata"), weak));
int D_009DFC00 __attribute__((section(".sdata"), weak));
void func_00106554(void){ int sp[8]; sp[1] = 1; sp[2] = 0; D_009DB7AC = eekernel_70(sp); D_009DFC00 = func_001064e0((void *)func_00106488, D_009E2790, 0x1000, 0x10, 0); func_00106408((void *)func_00106540); func_002b6a50((void *)func_001062e4); }
