struct S { char pad[4]; unsigned char *p; };
int func_00303d38(struct S *s, int *out)
{
  unsigned char *q = s->p;
  *out = 0;
  *out = (unsigned short)((q[0x12] << 8) + q[0x13]);
  return 1;
}
