/* func_00258230 @ 0x00258230 (36 B) : write two scaled values to p->a/b and p->c/d */
struct S {
  int a;        /* 0x0 */
  int b;        /* 0x4 */
  int c;        /* 0x8 */
  int d;        /* 0xC */
};

void func_00258230(struct S *p, int a, int b)
{
  int x = (a + 0x6C0) << 4;
  int y = (b + 0x720) << 4;
  p->a = x;
  p->b = y;
  p->c = x;
  p->d = y;
}
