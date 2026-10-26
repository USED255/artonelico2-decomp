extern char D_00BFF280[];
void func_002362c4(int i, int d){ if (i != -1) { unsigned char *p = (unsigned char *)((int)D_00BFF280 + i); int x = *p + d; if (x >= 0xFB) x = 0xFA; *p = x; } }
