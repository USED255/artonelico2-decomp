/* func_0032f0e0 : null-guard + field at +0x1B8 (CRI) */
struct S { char pad_0x0[0x1B8]; int f; };
extern char D_009D40A0[];
extern void func_00342ef8(void *);

int func_0032f0e0(struct S *p)
{
  if (!p)
  {
    func_00342ef8(D_009D40A0);
    return -1;
  }
  return p->f;
}
