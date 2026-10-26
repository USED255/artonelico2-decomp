extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_002072fc(char *a, int b, int c, int d){ char buf[0x10]; func_0021b834(buf); buf[8] = 0x35; *(int *)buf = d; *(short *)(buf + 4) = c; func_0021be98(a, (void *)(long)b, buf); }
