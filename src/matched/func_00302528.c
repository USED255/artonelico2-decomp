extern int func_00303480(void *, int);
extern int func_00304348(void *, int);
int func_00302528(char *p, int a)
{
  register int m asm("a3");
  int v = a & 0xFF;
  m = *(int *)(p + 0x10);
  switch (m) { case 0x64: return func_00303480(p, v); case 0xC8: return func_00304348(p, v); }
  return 0;
}
