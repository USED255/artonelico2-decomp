extern void func_00222670(void);
extern void func_00106194(void *);
extern void baseelf_10(void *);
extern void func_00322118(int);
extern char D_00A504E0[];
int func_002223b8(void){ func_00222670(); func_00106194(D_00A504E0); baseelf_10(D_00A504E0); func_00322118(0); __asm__ volatile ("sync"); __asm__ volatile ("ei"); return 0; }
