
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
M2C_UNK eekernel_110(M2C_UNK);
M2C_UNK func_002b5c00(M2C_UNK, M2C_UNK);
M2C_UNK func_002b76d8(s32, s32);
M2C_UNK func_002b7978(s32, M2C_UNK, M2C_UNK);
extern M2C_UNK D_00A50190;
void func_00137e70(s32 arg0)
{
  unsigned long new_var;
  eekernel_110(0);
  new_var = 0x330;
  func_002b7978(*((s32 *) (((s8 *) (&D_00A50190)) + new_var)), 0, 0);
  func_002b5c00(0, 0);
  func_002b76d8(*((s32 *) (((s8 *) (&D_00A50190)) + new_var)), arg0);
}
