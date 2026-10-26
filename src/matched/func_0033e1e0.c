struct S { char pad[0x10]; int f10; };
extern void func_003344a8(int, void *, int, int, int);
void func_0033e1e0(struct S *p){ int buf[1]; buf[0] = p->f10; func_003344a8(1, buf, 1, 0, 0); ((char *)p)[0] = 0; }
