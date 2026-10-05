
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
s32 func_001004b8();
s32 func_001004c0();
s32 func_001004c8();
extern s32 D_007EAD98;
extern s32 D_007EAD9C;
extern s32 D_007EADA0;
extern s32 D_007EB7C8;
void func_00247a34(void)
{
  int new_var;
  new_var = D_007EB7C8 > 0;
  if (new_var)
  {
    if (D_007EB7C8)
    {
      D_007EAD98 = func_001004b8();
      D_007EAD9C = func_001004c0();
      D_007EADA0 = func_001004c8();
    }
    else
    {
      D_007EAD98 = func_001004b8();
      D_007EAD9C = func_001004c0();
      D_007EADA0 = func_001004c8();
    }
  }
}
