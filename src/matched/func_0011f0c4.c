/* func_0011f0c4 @ 0x0011f0c4 (36 B) : write two scaled values to p->a/b and p->c/d */
struct S {
  char pad_0x0[4];
  int a;        /* 0x4 */
  int b;        /* 0x8 */
  int c;        /* 0xC */
  int d;        /* 0x10 */
};

void func_0011f0c4(struct S *p, int a, int b)
{
  int x = (a + 0x6C0) << 4;
  int y = (b + 0x720) << 4;
  p->a = x;
  p->b = y;
  p->c = x;
  p->d = y;
}
