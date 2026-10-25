/* func_003292b0 : null-guard + word at +0x14, returns 0 after init (CRI) */
struct S { char pad_0x0[0x14]; int f; };
extern char D_009D3588[];
extern void func_0031c878(void *);

int func_003292b0(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D3588);
    return 0;
  }
  return p->f;
}
