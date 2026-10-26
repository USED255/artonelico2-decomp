extern void func_002a5000(void *, void *, void *);
extern void func_00155be8(void);
extern void func_00155c24(void);
int D_009DCA10 __attribute__((section(".sdata"), weak));
void func_00155cc8(char *p){ if (D_009DCA10 != 0) return; func_002a5000((void *)func_00155be8, (void *)func_00155c24, p); }
