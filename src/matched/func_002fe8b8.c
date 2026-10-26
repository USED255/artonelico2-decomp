extern int func_002efef8(void *);
extern int func_002efcd8(int, int);
struct S { char pad[0x44]; int f44; };
int func_002fe8b8(struct S *p){ int *q; if (func_002efef8(p)) return func_002efcd8(0, 0xFF000122); q = (int *)((char *)p + 0xD88); q[0xA9] = q[0xA9] + 1; p->f44 = 1; return 0; }
