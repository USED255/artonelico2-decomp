/* func_002cb780 : init-on-zero wrapper around func_002caf80 (CRI, -O1) */
extern int func_002caf80(void);
extern void func_002cb2c8(int, int, int *);

int func_002cb780(void)
{
  int x = func_002caf80();
  if (x)
    return x;
  func_002cb2c8(0, 0, &x);
  return x;
}
