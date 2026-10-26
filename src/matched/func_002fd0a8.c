extern int func_002efef8(void *);
extern int func_002efcd8(int, int);
extern void func_002fd2b0(void *);
int func_002fd0a8(char *p, int a){ int *q; if (func_002efef8(p)) return func_002efcd8(0, 0xFF00015B); q = (int *)*(int *)(p + 0x3720); if (!q) return 0; q[0x374] = a; func_002fd2b0(p); return 0; }
