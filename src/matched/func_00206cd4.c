extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_00206cd4(char *a, int b, int c, int d){ char buf[0x10]; func_0021b834(buf); buf[8] = 0x11; *(int *)buf = 0x1D; *(short *)(buf + 4) = d; func_0021be98(a, (void *)(long)b, buf); }
