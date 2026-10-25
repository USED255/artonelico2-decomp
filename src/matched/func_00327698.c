/* func_00327698 : null-guard + signed byte at +0x1 (CRI) */
struct S { char pad_0x0[0x1]; signed char b; };
extern char D_009D3080[];
extern void func_0031c878(void *);

int func_00327698(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D3080);
    return -1;
  }
  return p->b;
}
