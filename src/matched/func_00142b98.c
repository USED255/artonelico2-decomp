extern void func_001205c0(void *, int, int);
extern void baseelf_161(void *, int);
void func_00142b98(char *p, int a){ char *q; func_001205c0(p + 0x3380, 0, a); q = (char *)a + (long)p; baseelf_161(p, *(short *)(p + 0x3786)); *(char *)(q + 0x4914) = 1; }
