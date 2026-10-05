
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
s32 func_001ab5d4(M2C_UNK, void *, void *, void *);
s32 func_001abcb0(void *arg0, M2C_UNK arg1)
{
  s32 var_t7;
  void *temp_s2;
  temp_s2 = arg0 + 0x20;
  var_t7 = 1;
  if (func_001ab5d4(arg1, arg0, arg0 + 0x10, temp_s2) == 0)
  {
    if ((*((s32 *) (((s8 *) arg0) + 0x50))) == 4)
    {
      return func_001ab5d4(arg1, temp_s2, arg0 + 0x30, arg0);
    }
    var_t7 = 0;
  }
  return var_t7;
}
