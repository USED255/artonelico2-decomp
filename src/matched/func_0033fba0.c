/* func_0033fba0 : null-guard + field at +0x4 (CRI) */
struct S { char pad_0x0[0x4]; int f; };
extern char D_009D70D0[];
extern void func_0033f150(void *);

int func_0033fba0(struct S *p)
{
  if (!p)
  {
    func_0033f150(D_009D70D0);
    return -1;
  }
  return p->f;
}
