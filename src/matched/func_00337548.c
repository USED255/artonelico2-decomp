/* func_00337548 : null-guard + field at +0x24 (CRI) */
struct S { char pad_0x0[0x24]; int f; };
extern char D_009D5B48[];
extern void func_00337b50(void *);

int func_00337548(struct S *p)
{
  if (!p)
  {
    func_00337b50(D_009D5B48);
    return -1;
  }
  return p->f;
}
