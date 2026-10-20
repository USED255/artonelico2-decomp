
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
M2C_UNK func_0013e2fc();
void func_0027ab84(void *arg0)
{
  u16 temp_t3;
  u16 temp_t4;
  u8 temp_t7;
  if ((*((s64 *) (((s8 *) arg0) + 0x40))) & 0x01000000)
  {
    func_0013e2fc();
    temp_t7 = *((u8 *) (((s8 *) arg0) + 0x42));
    if (((s8) temp_t7) > 0)
    {
      temp_t4 = *((u16 *) (((s8 *) arg0) + 6));
      temp_t3 = *((u16 *) (((s8 *) arg0) + 8));
      *((u16 *) (((s8 *) arg0) + 6)) = (u16) (temp_t4 + (((s32) ((*((s16 *) (((s8 *) arg0) + 0xA))) - ((s16) temp_t4))) / ((s8) temp_t7)));
      *((u16 *) (((s8 *) arg0) + 8)) = (u16) (temp_t3 + (((s32) ((*((s16 *) (((s8 *) arg0) + 0xC))) - ((s16) temp_t3))) / ((s8) temp_t7)));
      *((u8 *) (((s8 *) arg0) + 0x42)) = (u8) (temp_t7 - 1);
    }
  }
}
