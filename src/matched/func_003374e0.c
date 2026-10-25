/* func_003374e0 : null-guard + signed byte at +0x1 (CRI) */
struct S { char pad_0x0[0x1]; signed char b; };
extern char D_009D5B18[];
extern void func_00337b50(void *);

int func_003374e0(struct S *p)
{
  if (!p)
  {
    func_00337b50(D_009D5B18);
    return -1;
  }
  return p->b;
}
