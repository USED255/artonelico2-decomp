extern char D_00BC0940[];
extern void func_001d7db0(void *, int);
extern void func_001d7eec(void *, int);
void func_001a3b24(int v){ char *p = D_00BC0940; if (*(short *)(p + 0x10) == v) func_001d7db0(p + 4, v); else func_001d7eec(p + 4, v); }
