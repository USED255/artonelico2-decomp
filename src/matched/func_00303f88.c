/* func_00303f88 : big-endian pack of 4 bytes at p->f+0xD4 (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303f88(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xD4];
  v = (v << 8) + q[0xD5];
  v = (v << 8) + q[0xD6];
  v = (v << 8) + q[0xD7];
  *out = v;
  return 1;
}
