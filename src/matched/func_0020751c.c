extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_0020751c(char *a, int b, int c, int d){ char buf[0x10]; func_0021b834(buf); buf[8] = 0x24; *(int *)buf = c; *(short *)(buf + 4) = d; func_0021be98(a, (void *)(long)b, buf); }
