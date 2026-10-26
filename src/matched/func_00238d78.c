struct S { char pad[0x34]; short h34; short h36; };
extern void func_00238d94(void *);
void func_00238d78(struct S *p, int a, int b){ p->h36 = a; p->h34 = b; func_00238d94(p); }
