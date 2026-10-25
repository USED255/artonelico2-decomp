/* func_0024807c : clamp s16 at D+0x396+2*i to 0x7D00 (game) */
extern short D_00C082A8[];

void func_0024807c(int i, int v)
{
  if (i == -1)
    return;
  short *base = (short *)((char *)D_00C082A8 + i * 2);
  short *p = base + 0x1CB;
  int x = *p + v;
  if (x > 0x7D00)
    x = 0x7D00;
  *p = x;
}
