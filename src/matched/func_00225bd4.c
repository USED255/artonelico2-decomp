
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
extern void *D_007AF2D0;
void func_00225bd4(void *arg0, s32 arg1)
{
  s32 var_a1;
  s32 var_t5;
  var_a1 = arg1;
  if (((*((s16 *) (((s8 *) D_007AF2D0) + 0xC1C8A))) == 1) && (var_a1 > 0))
  {
    var_a1 = ((s32) (var_a1 * (*((s16 *) (((s8 *) D_007AF2D0) + 0xC1C8C))))) / 100;
  }
  var_a1 = var_a1 + (*((s32 *) (((s8 *) arg0) + 0x38)));
  *((s32 *) (((s8 *) arg0) + 0x38)) = (s32) (var_a1 % 100);
  var_t5 = (var_a1 / 100) + (*((s32 *) (((s8 *) arg0) + 0x34)));
  *((u32 *) (((s8 *) arg0) + 0x34)) = var_t5;
  if (var_t5 >= 0)
  {
    if (var_t5 > 0x98967F)
    {
      var_t5 = 0x98967F;
    }
  }
  else
  {
    var_t5 = 0;
  }
  *((u32 *) (((s8 *) arg0) + 0x34)) = var_t5;
}
