extern void func_002521bc(void *);
extern void func_00105e3c(void *, int);
extern void func_001358ac(int);
extern void baseelf_73(int, int);
extern void func_00107e48(int);
extern char D_00A504E0[];
int D_009DF410 __attribute__((section(".sdata")));
void func_0025097c(char *p){ D_009DF410 = 0; func_002521bc(p); func_00105e3c(D_00A504E0, 1); func_001358ac(1); baseelf_73(0, *(int *)(p + 0x8000 + 0x3978)); func_00107e48(0); }
