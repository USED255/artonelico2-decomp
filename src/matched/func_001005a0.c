
typedef signed char s8;
typedef unsigned char u8;
typedef short s16;
typedef unsigned short u16;
typedef int s32;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef unsigned char byte;
typedef unsigned char code;
typedef unsigned int uint;
typedef int s128;
typedef int u128;
typedef int s64_;
extern unsigned char *sp;
typedef s32 M2C_UNK;
typedef s8 M2C_UNK8;
typedef s16 M2C_UNK16;
typedef s32 M2C_UNK32;
typedef s64 M2C_UNK64;
s32 func_00360918(M2C_UNK, s32);
M2C_UNK func_00360b28(s32);
s32 func_001005a0(void)
{
  s32 temp_v0;
  s32 var_s0;
  s32 var_s1;
  s32 var_s2;
  var_s0 = 0x04000000;
  var_s2 = 0;
  var_s1 = 0x04000000;
  do
  {
    var_s1 = var_s2 + var_s0;
    temp_v0 = func_00360918(0x10, var_s1);
    if (temp_v0 != 0)
    {
      var_s2 = var_s1;
      func_00360b28(temp_v0);
    }
    var_s0 = var_s0 / 2;
  }
  while (var_s0 >= 0x400);
  return var_s2;
}
