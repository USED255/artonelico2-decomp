/* func_002e1d40 : call func_00301f30(x,&local); return local if it returns 1 else -1 (CRI) */
extern int func_00301f30(int, int *);

int func_002e1d40(int x)
{
  int l;
  int r = func_00301f30(x, &l);
  if (r == 1)
    return l;
  return -1;
}
