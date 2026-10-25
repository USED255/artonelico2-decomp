/* func_002cb680 : init-on-zero wrapper around func_002cac60 (CRI, -O1) */
extern int func_002cac60(void);
extern void func_002cb2c8(int, int, int *);

int func_002cb680(void)
{
  int x = func_002cac60();
  if (x)
    return x;
  func_002cb2c8(0, 0, &x);
  return x;
}
