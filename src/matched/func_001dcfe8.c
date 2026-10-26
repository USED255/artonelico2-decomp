int *D_009DE038 __attribute__((section(".sdata")));
int func_001dcfe8(int a, int b, int c){ int base = *(int *)(a * 12 + (int)D_009DE038 + 4); int mid = *(int *)(b * 16 + base); if (mid == 0) return -1; return *(short *)(c * 2 + mid); }
