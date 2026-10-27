extern int func_00303838(int);
int func_003037e0(int a, char *p){ int r = func_00303838(a); unsigned char v; int x; if (r != 0xC0) return 0; v = *(unsigned char *)(p + 0x20); x = (v != 0); if (v >= 2) x = 0; return x; }
