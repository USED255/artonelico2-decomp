
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
s32 func_001d8fb0(s16, M2C_UNK);
extern M2C_UNK D_007A0A00;
extern s8 D_00BC41E9;
void func_001d98b8(s32 arg0)
{
  s8 *new_var2;
  s8 *new_var;
  s8 *new_var3;
  new_var2 = &D_007A0A00;
  new_var3 = (s8 *) (((13 * arg0) * 4) + new_var2);
  new_var2 = new_var3 + 0x18;
  new_var = new_var2;
  if (func_001d8fb0(*((s16 *) new_var), 0) != (-1))
  {
    D_00BC41E9 = 1;
  }
  else
  {
    D_00BC41E9 = 0;
  }
}
