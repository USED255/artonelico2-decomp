extern int func_00303548(void *, int);
extern int func_00304508(void *, int);
int func_003025d8(char *p, int a)
{
  register int m asm("a3");
  int v = a & 0xFF;
  m = *(int *)(p + 0x10);
  switch (m) { case 0x64: return func_00303548(p, v); case 0xC8: return func_00304508(p, v); }
  return 0;
}
