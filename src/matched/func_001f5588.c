extern int baseelf_16(int);
int func_001f5588(char *a, int *c){ int idx = *c; if (!(idx < *(short *)(a + 0x20))) return 0; *c = *c + 1; return baseelf_16(*(short *)(a + idx * 2 + 0x18)); }
