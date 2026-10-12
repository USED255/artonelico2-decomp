
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
void func_0017ca74(s32 arg0)
{
  s32 temp_t7;
  s32 temp_t7_2;
  s32 var_t4;
  void *temp_t5;
  var_t4 = 0;
  do
  {
    temp_t7 = (var_t4 * 0x4C) + arg0;
    var_t4 += 1;
    temp_t5 = temp_t7 + 0x450;
    temp_t7_2 = *((s32 *) (((s8 *) temp_t5) + 4));
    temp_t7 = 0x1000;
    if (temp_t7_2 != 0)
    {
      *((s32 *) (((s8 *) temp_t5) + 4)) = (s32) (arg0 + ((temp_t7_2 * 4) - temp_t7));
    }
  }
  while (var_t4 < 0xA);
}
