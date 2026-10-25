/* func_0027395c @ 0x0027395c (20 B) : store (short)v at p+0xA and at D_003BFF18+0x98 */
struct S {
  char pad_0x0[0xA];
  short x;      /* 0xA */
};

struct G {
  char pad_0x0[0x98];
  short y;      /* 0x98 */
};

extern struct G D_003BFF18;

void func_0027395c(struct S *p, int v)
{
  p->x = (short)v;
  D_003BFF18.y = (short)v;
}
