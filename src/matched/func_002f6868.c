struct S { char pad[0x9A0]; long long q9A0; char pad2[0x2038 - 0x9A8]; int f2038; };
extern void func_002ed458(struct S *, int, int *);
extern void func_002edc38(int, int *, int *);
extern long long func_002eddf0(long long, int);
void func_002f6868(struct S *p){ int a, b, c; func_002ed458(p, p->f2038, &a); if (!a) return; func_002edc38(a, &b, &c); p->q9A0 = func_002eddf0(p->q9A0, b); }
