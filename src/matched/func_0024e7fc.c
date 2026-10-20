
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
s32 func_00191a08(s16);
extern volatile char D_007EB850;
s32 func_0024e7fc(s32 arg0)
{
  s32 var_v0;
  void *temp_s0;
  temp_s0 = (arg0 * 0x46) + (&D_007EB850);
  var_v0 = (func_00191a08(*((s16 *) (((s8 *) temp_s0) + 2))) > 0) || ((var_v0 = 0, (*((s16 *) (((s8 *) temp_s0) + 2))) == (-1)));
  if (var_v0)
  {
    var_v0 = 1;
  }
  return var_v0;
}
