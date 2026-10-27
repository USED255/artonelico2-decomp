extern char *D_009DFCD4;
extern void func_00180cec(int);
int func_00180f34(int i){ char *base = *(char **)&D_009DFCD4; char *q = base + i * 0xB0; int k; char *r; if (*(int *)q == 0) return 0; if (*(unsigned int *)(q + 0xC) >= 0xC8) return 0; k = *(int *)(q + 0x14); r = (char *)(k * 0xE0 + (int)base); *(short *)(r + 0x6A84) = 0; func_00180cec(i); return 1; }
