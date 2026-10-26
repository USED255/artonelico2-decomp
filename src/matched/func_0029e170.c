extern char D_00C0D378[];
int func_0029e170(int a, int b){ int i; for (i = 0; i < 0xA; i++) { char *p = (char *)(D_00C0D378 + i * 8); if (*(signed char *)(p + b + 4) != 0) { if (*(int *)p == a) return 1; } } return 0; }
