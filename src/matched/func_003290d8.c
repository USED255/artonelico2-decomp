/* func_003290d8 : null-guard + field at +0x4C (CRI) */
struct S { char pad_0x0[0x4C]; int f; };
extern char D_009D3528[];
extern void func_0031c878(void *);

int func_003290d8(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D3528);
    return -1;
  }
  return p->f;
}
