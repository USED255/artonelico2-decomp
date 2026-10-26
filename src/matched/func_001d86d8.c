struct S { int pad; short v; };
void func_001d86d8(char *p, int v){ int i = 0; do { struct S *q = (struct S *)(i * 6 + (int)p + 0x200); i = i + 1; q->v = v; } while (i < 0x1E); }
