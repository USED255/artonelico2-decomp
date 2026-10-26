/* func_00324ec8 @ 0x00324ec8 (28 B, CRI) : test bits 0xFF00 of the two u16 slots in a u64 at p+0x48 */
struct S {
  char pad_0x0[0x48];
  unsigned long long x;   /* 0x48 */
};

int func_00324ec8(struct S *p)
{
  return (p->x & 0x0000FF000000FF00ULL) != 0;
}
