extern char D_00BC0940[];
extern void func_001d8010(void *, int, int);
extern void func_001d7f74(void *, int, int);
void func_001a3b60(int v, int w){ char *p = D_00BC0940; if (*(short *)(p + 0x10) == v) func_001d8010(p + 4, v, w); else func_001d7f74(p + 4, v, w); }
