/* func_00303f50 : big-endian pack of 4 bytes at p->f+0xD0 (CRI) */
struct S { char pad_4[4]; unsigned char *f; };

int func_00303f50(struct S *p, int *out)
{
  unsigned char *q = p->f;
  unsigned v = q[0xD0];
  v = (v << 8) + q[0xD1];
  v = (v << 8) + q[0xD2];
  v = (v << 8) + q[0xD3];
  *out = v;
  return 1;
}
