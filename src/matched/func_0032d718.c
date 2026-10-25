/* func_0032d718 : null-guard tail call, else store low byte at +0x1B1 (CRI) */
struct S { char pad_0x0[0x1B1]; signed char b; };
extern char D_009D3C60[];
extern void func_00342ef8(void *);

void func_0032d718(struct S *p, int v)
{
  if (!p)
  {
    func_00342ef8(D_009D3C60);
    return;
  }
  p->b = v;
}
