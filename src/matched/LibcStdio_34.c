
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
M2C_UNK LibcString_6(s32, s32, s32);
s32 func_00362da0(void *);
u32 LibcStdio_34(s32 arg0, u32 arg1, u32 arg2, void *arg3)
{
  s32 var_a2;
  s32 var_s0;
  s32 var_s3;
  u32 temp_s6;
  u32 var_s2;
  u32 var_v0;
  var_v0 = 0;
  var_s2 = arg2 * arg1;
  if (var_s2 != 0)
  {
    var_a2 = *((s32 *) (((s8 *) arg3) + 4));
    if (var_a2 < 0)
    {
      *((s32 *) (((s8 *) arg3) + 4)) = 0;
      var_a2 = 0;
      var_s0 = 0;
    }
    var_s0 = var_a2;
    var_s3 = arg0;
    temp_s6 = var_s2;
    if (((u32) var_a2) < var_s2)
    {
      loop_4:
      var_s2 -= var_s0;

      LibcString_6(var_s3, *((s32 *) (((s8 *) arg3) + 0)), var_s0);
      var_s3 += var_s0;
      *((s32 *) (((s8 *) arg3) + 0)) = (s32) ((*((s32 *) (((s8 *) arg3) + 0))) + var_s0);
      if (func_00362da0(arg3) == 0)
      {
        var_s0 = *((s32 *) (((s8 *) arg3) + 4));
        if (((u32) var_s0) >= var_s2)
        {
          goto block_6;
        }
        goto loop_4;
      }
      var_v0 = ((u32) (temp_s6 - var_s2)) / arg1;
    }
    else
    {
      block_6:
      LibcString_6(var_s3, *((s32 *) (((s8 *) arg3) + 0)), (s32) var_s2);

      var_v0 = arg2;
      *((s32 *) (((s8 *) arg3) + 4)) = (s32) ((*((s32 *) (((s8 *) arg3) + 4))) - var_s2);
      *((s32 *) (((s8 *) arg3) + 0)) = (s32) ((*((s32 *) (((s8 *) arg3) + 0))) + var_s2);
    }
  }
  return var_v0;
}
