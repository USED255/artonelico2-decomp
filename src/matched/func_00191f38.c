
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
extern char D_00BB8D50;
s32 func_00191f38(u32 arg0, s32 arg1)
{
  u8 *temp_a0;
  u8 temp_t7;
  if (arg0 < 0x198U)
  {
    temp_a0 = arg0 + (&D_00BB8D50);
    temp_t7 = *temp_a0;
    if ((temp_t7 & 0xF) < arg1)
    {
      *temp_a0 = (temp_t7 & 0xF0) | (arg1 & 0xF);
      return 1;
    }
  }
  return 0;
}
