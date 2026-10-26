extern void func_002ff470(char *, int, int, int *, int);
int func_002ff2e8(char *p, int x, int y){ int out; if (*(int *)(p + 0xA44)) return 1; func_002ff470(p, x, y, &out, *(int *)(p + 0xABC)); return out; }
