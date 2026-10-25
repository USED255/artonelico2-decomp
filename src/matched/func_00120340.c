/* func_00120340 : store two s16 then tail-call */
struct S { char pad[0x400]; short a; short b; };
extern void func_00120360(struct S *, int, int);
void func_00120340(struct S *p, int x, int y){ p->b=x; p->a=y; func_00120360(p,x,y); }
