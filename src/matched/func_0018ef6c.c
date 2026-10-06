
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
extern char D_00BB8538;
s32 func_0018ef6c(s32 arg0)
{
  s32 var_v0;
  s8 *new_var;
  var_v0 = 0;
  if (arg0 != (-1))
  {
    new_var = (s8 *) ((arg0 * 0xC) + (&D_00BB8538));
    var_v0 = (*((s8 *) (new_var + 8))) + 1;
  }
  return var_v0;
}
