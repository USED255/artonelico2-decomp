struct S { char pad[0x8]; int f8; char pad2[0x14]; int f20; char pad3[4]; short *f28; };
void func_001249e8(struct S *p, short *q)
{
  short a = q[1];
  short b = q[3];
  int d = b - a + 1;
  int v = (p->f20 << 1) + (d << 4);
  p->f28 = q;
  p->f8 = v;
}
