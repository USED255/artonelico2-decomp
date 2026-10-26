struct S { int pad; int v; };
extern int D_007AF2D0;
int func_001e4030(unsigned int i){ char *base = (char *)D_007AF2D0; if (i < 0x1E) return ((struct S *)(i * 4 + (int)base + 0xC1CD0))->v; return 0; }
