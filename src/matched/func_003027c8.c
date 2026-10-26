extern int func_00303610(void *, int);
extern int func_003045d8(void *, int);
int func_003027c8(char *p, int a)
{
  register int m asm("a3");
  int v = a & 0xFF;
  m = *(int *)(p + 0x10);
  switch (m) { case 0x64: return func_00303610(p, v); case 0xC8: return func_003045d8(p, v); }
  return 0;
}
