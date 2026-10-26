struct S { char pad[0x988]; long long f988; char pad2[0xA04]; int f1394; };
extern void func_002edc38(int, int *, int *);
extern long long func_002eddf0(long long, int);
void func_002f1cc0(struct S *p){ int a, b; if (p->f1394) { func_002edc38(p->f1394, &a, &b); p->f988 = func_002eddf0(p->f988, a); } }
