
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
M2C_UNK func_001b0690(s16);
s32 func_001de9b0();
extern s32 D_0079C91C;
s32 func_001deb30(s32 arg0)
{
  s16 *temp_t5;
  s32 var_s0;
  s32 var_s1;
  void *temp_a0;
  var_s1 = 0;
  if (func_001de9b0() != 0)
  {
    var_s0 = 0;
    temp_a0 = D_0079C91C + (arg0 * 0x14);
    var_s0 = 0;
    if ((*((s8 *) (((s8 *) temp_a0) + 0xC))) > 0)
    {
      do
      {
        temp_t5 = (*((s32 *) (((s8 *) temp_a0) + 0x10))) + (var_s0 * 0x1C);
        var_s0 += 1;
        if ((*((s8 *) (((s8 *) temp_t5) + 2))) == 6)
        {
          var_s1 = 1;
          func_001b0690(*((s16 *) (((s8 *) temp_t5) + 0)));
        }
      }
      while (var_s0 < (*((s8 *) (((s8 *) temp_a0) + 0xC))));
    }
  }
  return var_s1;
}
