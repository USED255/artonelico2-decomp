extern void func_001da3e4(void *);
extern void func_001da3f8(void *, void *);
extern void func_00106194(void *);
extern void baseelf_10(void *);
extern char D_00A504E0[];
char *D_009DDFDC __attribute__((section(".sdata"), weak));
int func_001da22c(void){ char *p = D_009DDFDC; if (*(signed char *)(p + 0x22) != 0) { func_001da3e4(p); func_001da3f8(D_00A504E0, p); func_00106194(D_00A504E0); baseelf_10(D_00A504E0); } __asm__ volatile ("sync"); __asm__ volatile ("ei"); return 0; }
