extern int D_00832BF8, D_00832BF0;
void func_0033aab0(char *p, int idx, int v){ int x; if (D_00832BF8 != 1 || D_00832BF0 > 0) { x = (v < -0xF) ? -0xF : v; if (x >= 0x10) x = 0xF; *(int *)(p + idx * 4 + 0x40) = x; } }
