
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
s32 func_00104a68();
extern M2C_UNK D_00A38A88;
void func_00104adc(s32 arg0, s32 arg1)
{
  s32 temp_v0;
  u16 temp_t6;
  void *temp_v0_2;
  temp_v0 = func_00104a68();
  if (temp_v0 >= 0)
  {
    temp_v0_2 = (void *) ((u8 *) (&D_00A38A88) + temp_v0 * 0x18);
    ;
    *((s16 *) (((s8 *) temp_v0_2) + 8)) = 0;
    if ((((*((u16 *) (((s8 *) temp_v0_2) + 6))) & 0xFFFF) + arg1) <= 0xFFFE)
    {
      *((u16 *) (((s8 *) temp_v0_2) + 6)) = (u16) ((*((u16 *) (((s8 *) temp_v0_2) + 6))) + arg1);
    }
    else
    {
      *((u16 *) (((s8 *) temp_v0_2) + 6)) = -1U;
    }
  }
}
