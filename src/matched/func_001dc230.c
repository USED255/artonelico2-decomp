int D_009DE060 __attribute__((section(".sdata"), weak));
extern int func_001dcfbc(void);
extern int func_001dd1ac(int, int *, int *, int);
int func_001dc230(void){ int a, b; int r = 0; int *p; if (func_001dcfbc() != 1) return r; p = (int *)D_009DE060; if (*(signed char *)((char *)p + 1) != 0) return r; r = func_001dd1ac(*(short *)((char *)p + 2), &a, &b, 0); return r; }
