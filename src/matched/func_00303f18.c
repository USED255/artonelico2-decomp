/* func_00303f18 : big-endian pack of 4 bytes at p->f+0xCC (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303f18(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xCC];
  v = (v << 8) + q[0xCD];
  v = (v << 8) + q[0xCE];
  v = (v << 8) + q[0xCF];
  *out = v;
  return 1;
}
