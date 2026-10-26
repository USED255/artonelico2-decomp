extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_0020677c(char *a, int b, int c, int d, int e){ char buf[0x10]; func_0021b834(buf); buf[8] = 0x13; *(int *)buf = e; *(short *)(buf + 4) = c; *(short *)(buf + 6) = d; func_0021be98(a, (void *)(long)b, buf); }
