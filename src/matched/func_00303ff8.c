/* func_00303ff8 : big-endian pack of 4 bytes at p->f+0xDC (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303ff8(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xDC];
  v = (v << 8) + q[0xDD];
  v = (v << 8) + q[0xDE];
  v = (v << 8) + q[0xDF];
  *out = v;
  return 1;
}
