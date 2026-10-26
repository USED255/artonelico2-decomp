/* func_002b3c60 : call func_002a4278(a, &local, D_009CAD60) then return local (CRI, -G0) */
extern long long D_009CAD60;
extern int func_002a4278(int, int *, long long);

int func_002b3c60(int a)
{
  int l = 0;
  func_002a4278(a, &l, D_009CAD60);
  return l;
}
