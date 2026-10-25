/* func_0018cec0 @ 0x0018cec0 (16 B) : store a 16-bit value at D_00BB8518+0xC */
struct D_00BB8518_s {
  char pad_0x0[0xC];
  short value_0xc;
};

extern struct D_00BB8518_s D_00BB8518;

void func_0018cec0(int v)
{
  D_00BB8518.value_0xc = (short)v;
}
