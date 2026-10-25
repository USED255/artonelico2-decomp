/* func_00258a84 : byte shuffle then tail-call func_00258994 */
struct S { char a; char b; char c; char d; char e; };
extern void func_00258994(struct S *);
void func_00258a84(struct S *p){ p->c=0x10; p->b=p->d; func_00258994(p); }
