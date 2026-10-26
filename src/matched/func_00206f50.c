extern void func_0021b834(void *);
extern void func_0021be98(void *, void *, void *);
void func_00206f50(char *a, int b, int ch, int val){ char buf[0x10]; func_0021b834(buf); buf[8] = ch; *(int *)buf = val; func_0021be98(a, (void *)(long)b, buf); }
