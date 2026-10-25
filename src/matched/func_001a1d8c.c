/* func_001a1d8c @ 0x001a1d8c (16 B) : store a 16-bit value at D_00BC0940+0x32D8 */
struct D_00BC0940_s {
  char pad_0x0[0x32D8];
  short value_0x32d8;
};

extern struct D_00BC0940_s D_00BC0940;

void func_001a1d8c(int v)
{
  D_00BC0940.value_0x32d8 = (short)v;
}
