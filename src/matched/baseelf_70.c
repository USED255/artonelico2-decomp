
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
M2C_UNK func_00225bd4(s32, s32);
s32 func_00233d40(s32, M2C_UNK, M2C_UNK);
void baseelf_70(s32 arg0, s32 arg1, s32 arg2)
{
  s32 new_var;
  s32 *new_var2;
  s32 var_s0;
  var_s0 = arg1;
  if (arg2 != 0)
  {
    new_var2 = &arg2;
    var_s0 += ((s32) (var_s0 * func_00233d40(*new_var2, 0x27, 0))) / 100;
  }
  new_var = var_s0;
  func_00225bd4(arg0 + 0x70, new_var);
}
