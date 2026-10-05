
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
s32 func_00147dc8();
extern s32 D_009E3D04;
s32 func_00147e64(void)
{
  s32 temp_hi;
  int new_var;
  s32 var_v0;
  int new_var2;
  new_var = 0;
  var_v0 = -0x7D;
  temp_hi = ((s32) ((unsigned int) (D_009E3D04 + 1))) % 20;
  D_009E3D04 = temp_hi;
  new_var2 = temp_hi == new_var;
  if (new_var2)
  {
    if (D_009E3D04)
    {
      var_v0 = func_00147dc8();
    }
    else
    {
      var_v0 = func_00147dc8();
    }
  }
  return var_v0;
}
