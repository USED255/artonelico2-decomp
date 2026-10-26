struct S { int pad; int v; };
extern int D_007AF2D0;
void func_001e3fc8(unsigned int i, int v){ char *base = (char *)D_007AF2D0; if (i < 0x1E) ((struct S *)(i * 4 + (int)base + 0xC1CD0))->v = v; }
