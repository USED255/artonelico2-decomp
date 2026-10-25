/* func_00303ee0 : big-endian pack of 4 bytes at p->f+0xC8 (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303ee0(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xC8];
  v = (v << 8) + q[0xC9];
  v = (v << 8) + q[0xCA];
  v = (v << 8) + q[0xCB];
  *out = v;
  return 1;
}
