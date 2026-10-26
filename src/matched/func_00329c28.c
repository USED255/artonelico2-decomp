/* func_00329c28 : null-guard then tail-call func_003242d8(field at +0x4) (CRI) */
struct S { char pad_0x0[0x4]; int f; };
extern char D_009D36F8[];
extern void func_0031c878(void *);
extern int func_003242d8(int);

int func_00329c28(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D36F8);
    return -1;
  }
  return func_003242d8(p->f);
}
