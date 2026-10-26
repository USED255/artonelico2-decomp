/* func_002b39d8 : call func_002a4278(a, &local, D_009CAD58) then return local (CRI, -G0) */
extern long long D_009CAD58;
extern int func_002a4278(int, int *, long long);

int func_002b39d8(int a)
{
  int l = 0;
  func_002a4278(a, &l, D_009CAD58);
  return l;
}
