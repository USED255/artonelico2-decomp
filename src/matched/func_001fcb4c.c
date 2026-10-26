int func_001fcb4c(char *p, int a){ int r = 0; if (a == 1 || a == 3) r = 1; short v = *(short *)(p + r * 2 + 0x334); if (v == -1) return 0; int t = (v < 3); return !t; }
