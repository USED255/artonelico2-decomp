/* func_0031f9b0 @ 0x0031f9b0 (24 B, CRI) : return D_0083D240[i]->f (f at +0x8) */
struct S {
  char pad_0x0[8];
  int f;        /* 0x8 */
};

extern struct S *D_0083D240[];

int func_0031f9b0(int i)
{
  return D_0083D240[i]->f;
}
