/* func_00313168 @ 0x00313168 (28 B, CRI) : initialise p->f and the struct at p+0x8 */
struct Inner {
  int a;        /* 0x8 */
  int b;        /* 0xC */
  int c;        /* 0x10 */
};

struct S {
  char pad_0x0[4];
  int f;        /* 0x4 */
  struct Inner z;
};

void func_00313168(struct S *p, int a, int b, int c)
{
  struct Inner *q = &p->z;
  q->a = c;
  q->b = a;
  q->c = b;
  p->f = 1;
}
