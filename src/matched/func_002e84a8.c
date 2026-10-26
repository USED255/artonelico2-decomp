struct S { char pad[0x514]; };
extern void func_002e5c70(struct S *, int, int, int, int);
void func_002e84a8(struct S *p, int i){ int *q = (int *)((char *)p + 0x514); int v = q[i * 9]; func_002e5c70(p, v + 0xC0, 0, 0, 0); }
