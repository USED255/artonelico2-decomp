extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_00206a90(char *a){ char buf[0x10]; func_0021b834(buf); buf[8] = 0x10; *(short *)(buf + 4) = 2; *(long long *)(buf + 8) |= 1LL << 42; func_0021be98(a, a, buf); }
