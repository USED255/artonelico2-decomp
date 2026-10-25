/* func_003209e0 : null-guard then tail-call func_00337510(field at +0x94) (CRI) */
struct S { char pad_0x0[0x94]; int f; };
extern char D_009D2CC0[];
extern void func_0031c878(void *);
extern int func_00337510(int);

int func_003209e0(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D2CC0);
    return -1;
  }
  return func_00337510(p->f);
}
