extern unsigned char D_00AE04E8[];
int func_001a682c(int idx){ int x = (D_00AE04E8[idx / 8] >> (idx % 8)) & 1; return x != 0; }
