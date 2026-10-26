/* func_002b3958 @ 0x002b3958 (20 B) : return (int *)((char *)p + p[4]*4 + 0x20) (CRI 2.96) */
int *func_002b3958(int *p)
{
  int off = p[4] * 4 + 0x20;
  return (int *)((char *)p + off);
}
