/* func_002e1b00 : call func_00302110(x,&local); return local if it returns 1 else -1 (CRI) */
extern int func_00302110(int, int *);

int func_002e1b00(int x)
{
  int l;
  int r = func_00302110(x, &l);
  if (r == 1)
    return l;
  return -1;
}
