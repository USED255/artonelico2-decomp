
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
M2C_UNK func_0014907c(M2C_UNK, s32);
extern M2C_UNK D_007F7680;
void func_0025e4dc(s32 arg0)
{
  s32 var_s0;
  M2C_UNK *new_var;
  var_s0 = 0;
  do
  {
    new_var = (M2C_UNK *) (&D_007F7680);
    if ((*((s16 *) (((char *) new_var) + (var_s0 * 0xC) + 4))) == arg0)
    {
      func_0014907c(4, var_s0);
    }
    var_s0 += 1;
  }
  while (var_s0 < 0x64);
}
