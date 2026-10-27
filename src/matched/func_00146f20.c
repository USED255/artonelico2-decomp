extern char D_00585990[];
void func_00146f20(int i, int a, int b){ char *base = D_00585990; char *q = (char *)(i * 0x120 + (int)base); q = q + 0xC0; *(short *)(q + 6) = b; *(short *)(q + 4) = a; }
