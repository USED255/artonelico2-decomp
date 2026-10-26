struct S { char pad[0xC]; unsigned short f; };
extern int LibcStdio_10(struct S *);
int func_00362d70(struct S *p){ if ((p->f & 9) != 9) return 0; return LibcStdio_10(p); }
