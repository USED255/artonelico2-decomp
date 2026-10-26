/* func_002cb500 : init-on-zero wrapper around func_002ca4f8 (CRI, -O1) */
extern int func_002ca4f8(void);
extern void func_002cb2c8(int, int, int *);

int func_002cb500(void)
{
  int x = func_002ca4f8();
  if (x)
    return x;
  func_002cb2c8(0, 0, &x);
  return x;
}
