extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_00206c28(char *a, int b, int c, int d){ char buf[0x10]; if (*(short *)(a + 0x1A) != 1) return; func_0021b834(buf); buf[8] = 0x11; *(int *)buf = 0x1B; *(short *)(buf + 4) = c; func_0021be98(a, (void *)(long)b, buf); func_0021b834(buf); buf[8] = 0x11; *(int *)buf = 0x1C; *(short *)(buf + 4) = d; func_0021be98(a, (void *)(long)b, buf); }
