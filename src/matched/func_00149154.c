extern char D_00AF2470[];
void func_00149154(int i, int v){ char *b = D_00AF2470 + i * 2; unsigned short *q = (unsigned short *)(b + 0x220); int s = (int)q[3] + v; if (s > 0xFFFF) s = 0xFFFF; q[3] = (unsigned short)s; }
