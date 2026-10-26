extern int func_002fd698(void *, int);
void func_002ec1d8(void *p, int a){ void **q; if (!func_002fd698(p, 6)) return; q = *(void ***)((char *)p + 0x2184); if (q[5]) ((void (*)(void *, int))q[5])(p, a); }
