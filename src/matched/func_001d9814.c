
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
s32 func_0018fef4();
s32 func_001d9798();
s32 func_00235f00();
s32 func_001d9814(void)
{
  s32 temp_s0;
  int new_var;
  s32 temp_s0_2;
  s32 var_s1;
  s32 var_v0;
  var_s1 = 4;
  temp_s0 = func_00235f00() * 0xA;
  temp_s0_2 = (temp_s0 - func_0018fef4()) - 9;
  if (temp_s0_2 < 0x15)
  {
    var_s1 = 3;
    if (temp_s0_2 < 0xB)
    {
      var_s1 = 2;
      if (temp_s0_2 < (-0xB))
      {
        var_s1 = (new_var = temp_s0_2 < (-0x15)) == 0;
      }
    }
  }
  if (func_001d9798() < 2)
  {
    var_s1 = var_s1 + 1;
    if (var_s1 >= 0)
    {
      var_v0 = var_s1;
      if (var_s1 >= 5)
      {
        var_v0 = 4;
      }
    }
    else
    {
      var_v0 = 0;
    }
    var_s1 = var_v0;
  }
  return var_s1;
}
