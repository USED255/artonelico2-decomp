
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
M2C_UNK func_00135a6c();
extern M2C_UNK D_00AF0850;
void func_00137950(s32 arg0, s32 arg1)
{
  u32 *new_var2;
  s8 *new_var3;
  s8 *new_var;
  new_var = (s8 *) (&D_00AF0850);
  new_var3 = new_var + 0x1C;
  new_var2 = (u32 *) new_var3;
  *new_var2 = arg0;
  *((u32 *) (new_var + 0x20)) = arg1;
  func_00135a6c();
}
