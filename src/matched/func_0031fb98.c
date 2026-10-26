struct S { char pad[4]; void *f4; };
extern void *func_003263f0(void *);
void *func_0031fb98(struct S *p){ if (!p) return 0; if (!p->f4) return 0; return func_003263f0(p->f4); }
