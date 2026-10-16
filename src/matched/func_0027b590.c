
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
s16 func_0027b590(void *arg0)
{
  s16 var_v0;
  u16 temp_t7;
  var_v0 = -1;
  temp_t7 = (*((u16 *) (((s8 *) arg0) + 0x8FC))) - 1;
  *((s16 *) (((s8 *) arg0) + 0x40E)) = 0;
  *((u16 *) (((s8 *) arg0) + 0x8FC)) = (*((u16 *) (((s8 *) arg0) + 0x8FC))) - 1;
  *((u16 *) (((s8 *) arg0) + 0x8FE)) = (u16) ((*((u16 *) (((s8 *) arg0) + 0x8FE))) & 0xFFF8);
  if (((s16) temp_t7) >= 0)
  {
    var_v0 = *((s16 *) (((s8 *) ((((s16) temp_t7) * 2) + arg0)) + 0x8CE));
  }
  return var_v0;
}
