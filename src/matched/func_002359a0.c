
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
s32 func_00235b80();
extern volatile char D_007D89E0;
s32 func_002359a0(u32 arg0)
{
  int new_var;
  s32 temp_v0;
  s32 var_s0;
  var_s0 = 0;
  if (arg0 < 0x64U)
  {
    temp_v0 = func_00235b80();
    new_var = 0xC;
    loop_2:
    if (temp_v0 >= (*((s16 *) (((s8 *) ((((arg0 * 0x16) + var_s0) * 2) + (&D_007D89E0))) + new_var))))
    {
      var_s0 += 1;
      if (var_s0 < 4)
      {
        goto loop_2;
      }
    }

  }
  return var_s0;
}
