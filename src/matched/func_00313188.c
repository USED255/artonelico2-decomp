/* func_00313188 @ 0x00313188 (32 B, CRI) : copy the three words at p+0x8 to *o3, *o1, *o2 */
struct Inner {
  int a;        /* 0x8 */
  int b;        /* 0xC */
  int c;        /* 0x10 */
};

struct S {
  char pad_0x0[8];
  struct Inner z;
};

void func_00313188(struct S *p, int *o1, int *o2, int *o3)
{
  struct Inner *q = &p->z;
  *o3 = q->a;
  *o1 = q->b;
  *o2 = q->c;
}
