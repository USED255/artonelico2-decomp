extern short D_00AF29A8[];
void func_0014d468(int a, int b){ int i; for (i = 0; i < 0xA; i++) { short *p = (short *)(i * 4 + (int)D_00AF29A8); if (*p < 0) { p[0] = a; p[1] = b; return; } } }
