/* func_0032dac8 : null-guard + word at +0x1A8, returns 0 after init (CRI) */
struct S { char pad_0x0[0x1A8]; int f; };
extern char D_009D3D78[];
extern void func_00342ef8(void *);

int func_0032dac8(struct S *p)
{
  if (!p)
  {
    func_00342ef8(D_009D3D78);
    return 0;
  }
  return p->f;
}
