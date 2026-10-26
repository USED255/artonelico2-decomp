extern char D_00A505C0[];
int func_001081f4(int i, int v){ if (i > 0) return 0; char *p = (char *)(i * 0x3C + (int)D_00A505C0); char *q = p + 0x30; *(char *)(q + 8) = v; return (signed char)v; }
