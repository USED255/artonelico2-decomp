/* func_0032d988 : null-guard + word at +0x90, returns 0 after init (CRI) */
struct S { char pad_0x0[0x90]; int f; };
extern char D_009D3D28[];
extern void func_00342ef8(void *);

int func_0032d988(struct S *p)
{
  if (!p)
  {
    func_00342ef8(D_009D3D28);
    return 0;
  }
  return p->f;
}
