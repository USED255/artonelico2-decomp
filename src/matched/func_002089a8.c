extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_002089a8(char *a, int b, int sel){ char buf[0x10]; int v; func_0021b834(buf); switch (sel) { case 1: v = 3; break; case 2: v = 4; break; case 3: v = 5; break; case 4: v = 6; break; case 6: v = 7; break; default: return; } buf[8] = v; func_0021be98(a, (void *)(long)b, buf); }
