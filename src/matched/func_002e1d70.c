/* func_002e1d70 : call func_00301f80(x,&local); return local if it returns 1 else -1 (CRI) */
extern int func_00301f80(int, int *);

int func_002e1d70(int x)
{
  int l;
  int r = func_00301f80(x, &l);
  if (r == 1)
    return l;
  return -1;
}
