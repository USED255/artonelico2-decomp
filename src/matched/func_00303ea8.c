/* func_00303ea8 : big-endian pack of 4 bytes at p->f+0xC4 (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303ea8(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xC4];
  v = (v << 8) + q[0xC5];
  v = (v << 8) + q[0xC6];
  v = (v << 8) + q[0xC7];
  *out = v;
  return 1;
}
