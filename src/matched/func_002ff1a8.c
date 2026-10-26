extern int func_002efef8(void *);
extern int func_002efcd8(int, int);
extern char D_009D0C10[];
int func_002ff1a8(char *p, int *out){ int r; *out = -1; r = func_002efef8(p); if (r) return func_002efcd8(0, 0xFF00011B); { int idx = *(int *)(p + 0x920); if (idx) *out = *(int *)(D_009D0C10 + idx * 4); } return 0; }
