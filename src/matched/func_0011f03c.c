/* func_0011f03c @ 0x0011f03c (40 B) : write v and two scaled values to p->a..e */
struct S {
  int a;        /* 0x0 */
  int b;        /* 0x4 */
  int c;        /* 0x8 */
  int d;        /* 0xC */
  int e;        /* 0x10 */
};

void func_0011f03c(struct S *p, int v, int a, int b)
{
  p->a = v;
  int x = (a + 0x6C0) << 4;
  int y = (b + 0x720) << 4;
  p->b = x;
  p->c = y;
  p->d = x;
  p->e = y;
}
