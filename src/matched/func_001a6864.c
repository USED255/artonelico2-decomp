extern unsigned char D_00BC4DD0[];
int func_001a6864(int idx){ int x = (D_00BC4DD0[idx / 8] >> (idx % 8)) & 1; return x != 0; }
