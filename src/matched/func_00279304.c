/* func_00279304 : byte shuffle then tail-call func_00278d50 */
struct S { char a; char b; char c; char d; char e; };
extern void func_00278d50(struct S *);
void func_00279304(struct S *p){ p->c=0; p->a=p->d; func_00278d50(p); }
