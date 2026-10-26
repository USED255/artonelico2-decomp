/* func_0011f1f4 @ 0x0011f1f4 (52 B) : write four scaled arguments to p+0x14..p+0x20 */
struct S {
  char pad_0x0[0x14];
  int a;        /* 0x14 */
  int b;        /* 0x18 */
  int c;        /* 0x1C */
  int d;        /* 0x20 */
};

void func_0011f1f4(struct S *p, int v1, int v2, int v3, int v4)
{
  p->a = (v1 + 0x6C0) << 4;
  p->b = (v2 + 0x720) << 4;
  p->c = (v3 + 0x6C0) << 4;
  p->d = (v4 + 0x720) << 4;
}
