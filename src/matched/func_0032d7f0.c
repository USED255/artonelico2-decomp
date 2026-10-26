/* func_0032d7f0 : null-guard + field at +0x1C0 (CRI) */
struct S { char pad_0x0[0x1C0]; int f; };
extern char D_009D3CB0[];
extern void func_00342ef8(void *);

int func_0032d7f0(struct S *p)
{
  if (!p)
  {
    func_00342ef8(D_009D3CB0);
    return -1;
  }
  return p->f;
}
