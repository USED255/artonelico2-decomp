/* func_00329320 : null-guard tail call, else store low byte at +0x70 (CRI) */
struct S { char pad_0x0[0x70]; signed char b; };
extern char D_009D35B8[];
extern void func_0031c878(void *);

void func_00329320(struct S *p, int v)
{
  if (!p)
  {
    func_0031c878(D_009D35B8);
    return;
  }
  p->b = v;
}
