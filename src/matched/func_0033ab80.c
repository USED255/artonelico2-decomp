/* func_0033ab80 : guard+tail with return 0 (CRI, -G0) */
extern int D_00832BF8;
extern int D_00832BF0;
extern char D_009D65D8[];
extern void func_003229d0(void *);

int func_0033ab80(void)
{
  if (D_00832BF8 == 1 && D_00832BF0 <= 0)
    return 0;
  func_003229d0(D_009D65D8);
  return 0;
}
