struct S { char pad[0xB8]; int fB8; };
struct T { char pad[0x50]; int f50, f54; char pad2[0]; int f58, f5C; };
extern void func_00305bf8(int, int *, int *);
void func_002e6168(struct S *p, int x, struct T *t){ int a, b; func_00305bf8(p->fB8, &a, &b); t->f58 = 0; t->f50 = a; t->f54 = b; t->f5C = 0; }
