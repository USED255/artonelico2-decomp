/* func_0032d300 : null-guard + signed byte at +0x1 (CRI) */
struct S { char pad_0x0[0x1]; signed char b; };
extern char D_009D3B88[];
extern void func_00342ef8(void *);

int func_0032d300(struct S *p)
{
  if (!p)
  {
    func_00342ef8(D_009D3B88);
    return -1;
  }
  return p->b;
}
