/* func_002b39a8 : call func_002a4278(a, &local, D_009CAD50) then return local (CRI, -G0) */
extern long long D_009CAD50;
extern int func_002a4278(int, int *, long long);

int func_002b39a8(int a)
{
  int l = 0;
  func_002a4278(a, &l, D_009CAD50);
  return l;
}
