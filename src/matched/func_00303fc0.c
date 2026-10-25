/* func_00303fc0 : big-endian pack of 4 bytes at p->f+0xD8 (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303fc0(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xD8];
  v = (v << 8) + q[0xD9];
  v = (v << 8) + q[0xDA];
  v = (v << 8) + q[0xDB];
  *out = v;
  return 1;
}
