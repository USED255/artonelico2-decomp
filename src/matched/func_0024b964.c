/* func_0024b964 : store two s16 then tail-call */
struct S { char pad[0xC0]; short a; short b; };
extern void func_0011f0c4(struct S *, int, int);
void func_0024b964(struct S *p, int x, int y){ p->a=x; p->b=y; func_0011f0c4(p,x,y); }
