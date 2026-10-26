extern char D_009D14C0[];
extern void func_00305a10(int, int, void *);
int func_00306e10(int a){ int r; if (a == 0x10) r = 1; else if ((unsigned)a < 0x11) { func_00305a10(0, 0, D_009D14C0); r = 0; } else if (a == 0x18) r = 2; else if (a == 0x20) r = 3; else { func_00305a10(0, 0, D_009D14C0); r = 0; } return r; }
