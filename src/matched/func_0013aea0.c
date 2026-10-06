
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
s32 func_0013aea0(void *arg0)
{
  s32 temp_t2;
  s32 temp_t4;
  s32 temp_t4_2;
  s32 temp_t5;
  s32 temp_t5_2;
  temp_t2 = *((s32 *) (((s8 *) arg0) + 0x10));
  if (temp_t2 != 0)
  {
    temp_t5 = *((s32 *) (((s8 *) arg0) + 0x1C));
    temp_t4 = *((s32 *) (((s8 *) arg0) + 0x20));
    temp_t5_2 = temp_t5 + (((s32) ((*((s32 *) (((s8 *) arg0) + 0x24))) - temp_t5)) / temp_t2);
    *((u32 *) (((s8 *) arg0) + 0x1C)) = temp_t5_2;
    temp_t4 = temp_t4 + (((s32) ((*((s32 *) (((s8 *) arg0) + 0x28))) - temp_t4)) / temp_t2);
    *((s32 *) (((s8 *) arg0) + 0x10)) = (s32) (temp_t2 - 1);
    *((s32 *) (((s8 *) arg0) + 0x14)) = (s32) (temp_t5_2 >> 4);
    temp_t4_2 = temp_t4;
    *((u32 *) (((s8 *) arg0) + 0x20)) = temp_t4_2;
    *((s32 *) (((s8 *) arg0) + 0x18)) = (s32) (temp_t4_2 >> 4);
  }
  return *((s32 *) (((s8 *) arg0) + 0x10));
}
