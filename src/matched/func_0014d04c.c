extern short D_00AF2818[];
void func_0014d04c(int a, int b){ int i; for (i = 0; i < 0x64; i++) { short *p = (short *)(i * 4 + (int)D_00AF2818); if (*p < 0) { p[0] = a; p[1] = b; return; } } }
