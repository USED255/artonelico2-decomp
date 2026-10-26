extern int func_003035d0(void *, int);
extern int func_00304598(void *, int);
int func_00302770(char *p, int a)
{
  register int m asm("a3");
  int v = a & 0xFF;
  m = *(int *)(p + 0x10);
  switch (m) { case 0x64: return func_003035d0(p, v); case 0xC8: return func_00304598(p, v); }
  return 0;
}
