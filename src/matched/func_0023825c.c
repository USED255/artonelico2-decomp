
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
M2C_UNK func_00238788(s32, s32, s32);
M2C_UNK func_00238818(s32);
M2C_UNK func_0024fbfc(s32);
s32 func_0024fd68(s32);
s32 func_0024fde8(s32);
void func_0023825c(s32 arg0)
{
  s32 temp_s0;
  s32 temp_s1;
  s32 temp_s2;
  temp_s0 = arg0 + 0x440;
  ;
  func_0024fbfc(temp_s0);
  temp_s2 = func_0024fd68(temp_s0);
  func_00238788(arg0 + 0x420, temp_s2, func_0024fde8(temp_s0));
  func_00238818(arg0 + 0x420);
}
