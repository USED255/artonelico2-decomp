/* func_00329bb8 : null-guard then tail-call func_003242e0(field at +0x4) (CRI) */
struct S { char pad_0x0[0x4]; int f; };
extern char D_009D36C8[];
extern void func_0031c878(void *);
extern int func_003242e0(int);

int func_00329bb8(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D36C8);
    return -1;
  }
  return func_003242e0(p->f);
}
