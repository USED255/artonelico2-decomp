/* func_002f7f20 @ 0x002f7f20 (28 B, CRI) : null-check then compare the s32 at +0x38 */
struct S {
  char pad_0x0[0x38];
  int f;        /* 0x38 */
};

int func_002f7f20(struct S *a, struct S *b)
{
  if (!a)
    return 1;
  return a->f > b->f;
}
