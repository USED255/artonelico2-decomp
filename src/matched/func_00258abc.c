/* func_00258abc : byte shuffle then tail-call func_00258994 */
struct S { char a; char b; char c; char d; char e; };
extern void func_00258994(struct S *);
void func_00258abc(struct S *p){ p->c=0; p->a=p->d; func_00258994(p); }
