extern int D_00587128[];
int func_001490c4(int i, int b){ unsigned char *p = (unsigned char *)(D_00587128[i] + b / 8); return (p[0] >> (b % 8)) & 1; }
