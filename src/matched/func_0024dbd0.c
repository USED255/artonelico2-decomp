struct S { char pad[0x40E]; unsigned short n; };
extern char D_0098F370[];
extern void func_001409d0(void *, int, int, int, int, int, int);
void func_0024dbd0(struct S *p){ p->n++; func_001409d0(D_0098F370, 9, -1, -1, -1, -1, 1); }
