
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
s32 func_001b7c90(s32);
extern M2C_UNK D_00BC6790;
s32 func_001b0cac(void)
{
  s32 temp_t7;
  s32 temp_t7_2;
  s32 var_s0;
  s32 var_t7;
  var_s0 = 0;
  var_s0 = var_s0 * 4;
  loop_1:
  temp_t7 = var_s0;

  var_s0 += 1;
  temp_t7_2 = *(temp_t7 + (&D_00BC6790));
  if ((temp_t7_2 == 0) || ((var_t7 = 1, func_001b7c90(temp_t7_2) == 0)))
  {
    if (1)
    {
    }
    if (var_s0 >= 0x1E)
    {
      var_t7 = 0;
    }
    else
    {
      goto loop_1;
    }
  }
  return var_t7;
}
