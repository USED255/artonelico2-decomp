
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
void func_0026b1f4(void *arg0)
{
  s32 temp_t5;
  s32 temp_t6;
  s32 temp_t7;
  s32 temp_t7_2;
  u16 temp_t4;
  temp_t4 = *((u16 *) (((s8 *) arg0) + 0x24));
  if (((s16) temp_t4) == (-1))
  {
    temp_t7 = (*((u32 *) (((s8 *) arg0) + 0)) = *((s32 *) (((s8 *) arg0) + 0x18)));
    temp_t6 = *((s32 *) (((s8 *) arg0) + 0x1C));
    *((u32 *) (((s8 *) arg0) + 8)) = temp_t7;
    *((u32 *) (((s8 *) arg0) + 4)) = temp_t6;
    *((u32 *) (((s8 *) arg0) + 0xC)) = temp_t6;
  }
  else
    if (((s16) temp_t4) < 4)
  {
    temp_t7_2 = *((s32 *) (((s8 *) arg0) + 0x10));
    temp_t5 = *((s32 *) (((s8 *) arg0) + 0x14));
    *((u16 *) (((s8 *) arg0) + 0x24)) = (u16) (temp_t4 + 4);
    *((u32 *) (((s8 *) arg0) + 0)) = temp_t7_2;
    *((u32 *) (((s8 *) arg0) + 8)) = temp_t7_2;
    *((u32 *) (((s8 *) arg0) + 4)) = temp_t5;
    *((u32 *) (((s8 *) arg0) + 0xC)) = temp_t5;
  }
  *((s16 *) (((s8 *) arg0) + 0x22)) = 0;
}
