extern char *func_002b73a8(int);
extern int func_002b7878(void *, int, int);
int func_002e4228(int a, int b, int c){ char *p = func_002b73a8(8); int v = b; *(int *)(p + 0x80) = a; if (b < 0) v = b + 0xF; func_002b7878(p, c, v >> 4); return 0; }
