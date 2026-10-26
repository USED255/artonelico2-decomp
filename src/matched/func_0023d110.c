extern void baseelf_171(void *);
extern void baseelf_104(void *);
extern void baseelf_49(void);
extern int D_009DFCD4;
char *D_009DF2A0 __attribute__((section(".sdata")));
void func_0023d110(void){ char *p = D_009DF2A0; char *q; baseelf_171(p); D_009DF2A0 = *(char **)(p + 0x1A50); baseelf_104(p); if (D_009DFCD4 != 0) baseelf_49(); q = D_009DF2A0; if (q != 0) { *(short *)(q + 0x1346) = -1; *(short *)(q + 0x1348) = -1; } }
