/* func_0031f540 : null-guard + field at +0x1C (CRI) */
struct S { char pad_0x0[0x1C]; int f; };
extern char D_009D2948[];
extern void func_0031c878(void *);

int func_0031f540(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D2948);
    return -3;
  }
  return p->f;
}
