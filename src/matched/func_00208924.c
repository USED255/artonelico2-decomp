extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_00208924(char *a, int b, int c, int d, int e, int f){ char buf[0x10]; func_0021b834(buf); buf[8] = c; *(short *)(buf + 4) = e; *(int *)buf = d; buf[9] = f; func_0021be98(a, (void *)(long)b, buf); }
