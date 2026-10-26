/* func_002cb640 : init-on-zero wrapper around func_002cab68 (CRI, -O1) */
extern int func_002cab68(void);
extern void func_002cb2c8(int, int, int *);

int func_002cb640(void)
{
  int x = func_002cab68();
  if (x)
    return x;
  func_002cb2c8(0, 0, &x);
  return x;
}
