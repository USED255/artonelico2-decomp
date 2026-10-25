/* deci2api_5 @ deci2api : eekernel_139(2, &x) where x is the single argument */
extern void eekernel_139(int, void *);

void deci2api_5(int a)
{
  int x = a;
  eekernel_139(2, &x);
}
