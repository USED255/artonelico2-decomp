struct S { char pad[4]; unsigned char *p; };
int func_00303c00(struct S *s, int *o1, int *o2)
{
  unsigned char *q = s->p + 0x20;
  *o1 = 0;
  *o2 = 0;
  *o1 = q[0x1A];
  *o2 = q[0x1B];
  return 1;
}
