extern int func_002fd698(void *, int);
extern void func_002ec3d0(void *);
int func_002ec390(char *p){ char *q; if (!func_002fd698(p, 6)) return 0; q = p + 0x36CC; *(int *)(p + 0x2184) = (int)q; func_002ec3d0(q); return 0; }
