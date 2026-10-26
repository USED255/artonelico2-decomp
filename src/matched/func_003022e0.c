extern int func_003032a8(void *, int);
extern int func_00304050(void *, int);
int func_003022e0(char *p, int a)
{
  register int m asm("a3");
  int v = a & 0xFF;
  m = *(int *)(p + 0x10);
  switch (m) { case 0x64: return func_003032a8(p, v); case 0xC8: return func_00304050(p, v); }
  return 0;
}
