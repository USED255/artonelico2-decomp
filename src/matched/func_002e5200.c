struct S { char pad[0x48]; int f; };
extern void func_002fbaf8(int, int *);
int func_002e5200(struct S *p){ int buf[8]; func_002fbaf8(p->f, buf); return buf[1] + buf[3]; }
