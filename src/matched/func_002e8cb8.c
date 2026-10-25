/* func_002e8cb8 @ 0x002e8cb8 (20 B, CRI) : &D_00818118[i] (8-byte elements) */
struct S {
  int a;
  int b;
};

extern struct S D_00818118[];

struct S *func_002e8cb8(int i)
{
  return &D_00818118[i];
}
