/* func_00298318 @ 0x00298318 (28 B) : decrement p->n (u16 at +0x54), return (s16)p->n == 0 */
struct S {
  char pad_0x0[0x54];
  unsigned short n;   /* 0x54 */
};

int func_00298318(int unused, struct S *p)
{
  p->n--;
  return (short)p->n == 0;
}
