/* func_003379d0 : null-guard + field at +0x14 (CRI) */
struct S { char pad_0x0[0x14]; int f; };
extern char D_009D5D50[];
extern void func_00337b50(void *);

int func_003379d0(struct S *p)
{
  if (!p)
  {
    func_00337b50(D_009D5D50);
    return -1;
  }
  return p->f;
}
