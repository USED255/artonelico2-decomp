extern int D_00832BF8;
extern int D_00832BF0;
struct S { char pad[1]; signed char b1; char pad2[0x54]; signed char b56; };
void func_00339ad0(struct S *p, int v){ if (D_00832BF8 == 1 && D_00832BF0 <= 0) return; if ((unsigned)v >= 2) return; if (p->b56 == v) return; p->b1 = p->b56; p->b56 = v; }
