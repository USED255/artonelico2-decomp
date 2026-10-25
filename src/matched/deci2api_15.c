/* deci2api_15 @ deci2api : eekernel_139(0x21, &x) where x is the single argument */
extern void eekernel_139(int, void *);

void deci2api_15(int a)
{
  int x = a;
  eekernel_139(0x21, &x);
}
