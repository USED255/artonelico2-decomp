/* func_00236374 @ 0x00236374 (36 B) : add a to the s16 at D_00BFF280+0x16A, clamp to 0x7530 */
struct G {
  char pad_0x0[0x16A];
  short v;      /* 0x16A */
};

extern struct G D_00BFF280;

void func_00236374(int a)
{
  int v = D_00BFF280.v + a;
  if (v > 0x7530)
    v = 0x7530;
  D_00BFF280.v = (short)v;
}
