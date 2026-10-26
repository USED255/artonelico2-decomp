extern unsigned char D_00AF14B8[];
void func_00140944(int a, int b){ unsigned char *base = D_00AF14B8; int idx = *((int *)(base + 0xE4C)); if (idx >= 0) { unsigned char *tmp = base + 0x10; unsigned offset = ((unsigned) idx) * 0x2DC; unsigned char *ptr = tmp + offset; ptr[0] = (unsigned char) a; ptr[1] = (unsigned char) b; } }
