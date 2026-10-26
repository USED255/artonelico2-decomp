/* func_002792c0 : byte shuffle then tail-call func_00278d50 */
struct S { char a; char b; char c; char d; char e; };
extern void func_00278d50(struct S *);
void func_002792c0(struct S *p){ p->c=0x10; p->b=p->d; func_00278d50(p); }
