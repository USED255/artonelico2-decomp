int func_00329d78(unsigned short *p, int len, int *out){ unsigned short v; if (len < 2) return 0; v = *p; v = (unsigned short)((v << 8) | (v >> 8)); if (v != 0x8001) return 0; *out = len; return 1; }
