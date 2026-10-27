extern int baseelf_16(int);
int func_001f55cc(char *a, int *c){ int idx = *c; if (!(idx < *(short *)(a + 0x14))) return 0; *c = *c + 1; return baseelf_16(*(short *)(a + idx * 2 + 4)); }
