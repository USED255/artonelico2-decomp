/* func_001b079c : loop over 0x1e ints at D_00BC6790+0x0, call func_001b793c for non-zero (game, -Os) */
extern int D_00BC6790[];
extern void func_001b793c(int);

void func_001b079c(void)
{
  int i, v;
  for (i = 0; i < 0x1e; i++)
  {
    v = D_00BC6790[i];
    if (v)
      func_001b793c(v);
  }
}
