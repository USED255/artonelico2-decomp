/* func_00337ab8 : null-guard tail call, else store low byte at +0x3 (CRI) */
struct S { char pad_0x0[0x3]; signed char b; };
extern char D_009D5D80[];
extern void func_00337b50(void *);

void func_00337ab8(struct S *p, int v)
{
  if (!p)
  {
    func_00337b50(D_009D5D80);
    return;
  }
  p->b = v;
}
