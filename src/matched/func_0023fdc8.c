/* func_0023fdc8 @ 0x0023fdc8 (36 B) : write D_00C06E78[i].a (s8) and .b (int at +0x4) */
struct S {
  signed char a;    /* 0x0 */
  char pad_0x1[3];
  int b;            /* 0x4 */
};

extern struct S D_00C06E78[];

void func_0023fdc8(int i, signed char c, int v)
{
  D_00C06E78[i].a = c;
  D_00C06E78[i].b = v;
}
