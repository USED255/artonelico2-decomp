/* func_001b0fc0 : loop over 0x1e ints at D_00BC6790+0x0, call func_001b0f7c for non-zero (game, -Os) */
extern int D_00BC6790[];
extern void func_001b0f7c(int);

void func_001b0fc0(void)
{
  int i, v;
  for (i = 0; i < 0x1e; i++)
  {
    v = D_00BC6790[i];
    if (v)
      func_001b0f7c(v);
  }
}
