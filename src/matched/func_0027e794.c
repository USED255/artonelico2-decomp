
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
s32 func_0027e794(s32 arg0)
{
  s32 var_t5;
  s32 var_v0;
  void *temp_t7;
  var_t5 = 0;
  loop_1:
  temp_t7 = (var_t5 * 0x2C) + arg0;

  var_v0 = 1;
  var_t5 += 1;
  if ((*((s32 *) (((s8 *) temp_t7) + 0x10))) == 0)
  {
    if (var_t5 >= 4)
    {
      var_v0 = 0;
    }
    else
    {
      goto loop_1;
    }
  }
  return var_v0;
}
