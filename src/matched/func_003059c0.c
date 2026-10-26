extern void func_00306110(void *);
extern void func_00313080(void *);
extern volatile int D_008183D0[];
void func_003059c0(char *p){ if (p) { void *a = *(void **)(p + 0x24); void *b = *(void **)(p + 0x30); *(int *)p = 0; func_00306110(a); func_00313080(b); D_008183D0[0] = D_008183D0[0] - 1; } }
