/* func_0032e790 : null-guard + word at +0x1E8, returns 0 after init (CRI) */
struct S { char pad_0x0[0x1E8]; int f; };
extern char D_009D3F40[];
extern void func_00342ef8(void *);

int func_0032e790(struct S *p)
{
  if (!p)
  {
    func_00342ef8(D_009D3F40);
    return 0;
  }
  return p->f;
}
