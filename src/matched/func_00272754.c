
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
s32 func_00272754(void *arg0, long long arg1)
{
  s32 var_v0;
  u8 temp_t6;
  var_v0 = -1;
  if (arg1 != (-1))
  {
    temp_t6 = *((u8 *) (((s8 *) arg0) + 0x4F5));
    var_v0 = 0;
    if (((s8) temp_t6) > 0)
    {
      loop_3:
      if ((*((s8 *) (((s8 *) ((var_v0 * 0x18) + arg0)) + 0x1C))) != arg1)
      {
        var_v0 += 1;
        if (var_v0 >= ((s8) temp_t6))
        {
          goto block_5;
        }
        goto loop_3;
      }

    }
    else
    {
      block_5:
      var_v0 = -1;

    }
  }
  return var_v0;
}
