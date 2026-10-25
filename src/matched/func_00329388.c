/* func_00329388 : null-guard + signed byte at +0x71 (CRI) */
struct S { char pad_0x0[0x71]; signed char b; };
extern char D_009D35F0[];
extern void func_0031c878(void *);

int func_00329388(struct S *p)
{
  if (!p)
  {
    func_0031c878(D_009D35F0);
    return -1;
  }
  return p->b;
}
