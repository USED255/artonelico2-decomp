
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
s32 func_002359a0();
s32 func_00235b80(u32);
extern M2C_UNK D_007D89E0;
s32 func_00235a1c(u32 arg0, s32 arg1)
{
  s32 temp_s3;
  s32 temp_v0;
  s32 var_s1;
  M2C_UNK *new_var;
  s32 var_t7;
  s32 var_v0;
  var_s1 = 0;
  if (arg0 < 0x64U)
  {
    temp_s3 = func_002359a0();
    temp_v0 = func_00235b80(arg0) + arg1;
    loop_2:
    var_t7 = temp_s3 < var_s1;

    new_var = &D_007D89E0;
    if (temp_v0 >= (*((s16 *) ((((char *) new_var) + (((arg0 * 0x16) + var_s1) * 2)) + 0xC))))
    {
      var_s1 += 1;
      if (var_s1 >= 4)
      {
        ;
      }
      else
      {
        goto loop_2;
      }
    }
    var_v0 = var_s1;
    if ((temp_s3 < var_s1) == 0)
    {
      goto block_6;
    }
  }
  else
  {
    block_6:
    var_v0 = 0;

  }
  return var_v0;
  var_t7 += 0;
}
