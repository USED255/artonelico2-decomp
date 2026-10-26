struct S { char pad[0x18]; int f18; char pad2[0x18]; int f34; };
void func_003252d8(struct S *p, int v){ if (v >= 0) p->f34 = v; else p->f34 = p->f18; }
