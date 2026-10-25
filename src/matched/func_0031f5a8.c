/* func_0031f5a8 : null-guard + signed byte at +0x1 (CRI) */
struct S { char pad_0x0[0x1]; signed char b; };
extern char D_009D2978[];
extern void func_0031c878(void *);

int func_0031f5a8(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D2978);
    return -3;
  }
  return p->b;
}
