/* func_00184efc @ 0x00184efc (20 B) : store two shorts and two bytes into a struct
 *
 * ee-gcc reorders the stores by size, so the source writes bytes first and the
 * target emits the two halfword stores before the two byte stores.
 */
struct S {
  char pad_0x0[0xFAC];
  short a;      /* 0xFAC */
  short b;      /* 0xFAE */
  char c;       /* 0xFB0 */
  char pad_0xfb1[0xE];
  char d;       /* 0xFBF */
};

void func_00184efc(struct S *p, int a, int b)
{
  p->c = (char)a;
  p->d = (char)b;
  p->a = (short)a;
  p->b = (short)b;
}
