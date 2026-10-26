struct S { char pad[4]; char *f4; char pad2[4]; int fC; };
int func_00303120(struct S *p, int *out){ if (p->fC < 0xE1) return 0; *out = *(int *)(p->f4 + 0xC4); return 1; }
