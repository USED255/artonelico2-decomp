/* func_001b5eb4 : loop over 0x80 ints at D_00BC6790+0x2078, call func_001ccc60 for non-zero (game, -Os) */
struct S { char pad_0x0[0x2078]; int arr[0x80]; };
extern struct S D_00BC6790;
extern void func_001ccc60(int);

void func_001b5eb4(void)
{
  int i, v;
  for (i = 0; i < 0x80; i++)
  {
    v = D_00BC6790.arr[i];
    if (v)
      func_001ccc60(v);
  }
}
