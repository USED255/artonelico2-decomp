/* iopldfl_5 @ 0x002c48c8 (28 B) : call func_002c42f8 with a 16-byte stack buffer */
extern void func_002c42f8(int, int, int, void *);

void iopldfl_5(int a, int b, int c)
{
  char buf[0x10];
  func_002c42f8(a, b, c, buf);
}
