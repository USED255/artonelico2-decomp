extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_00206bd0(char *a, int b, int c){ char buf[0x10]; func_0021b834(buf); buf[8] = 0x12; *(int *)buf = 8; *(short *)(buf + 4) = c; func_0021be98(a, a, buf); }
