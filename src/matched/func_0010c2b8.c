
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
M2C_UNK func_00109e5c(void *);
M2C_UNK func_0010bf4c(s32);
M2C_UNK func_0010c1ec(void *);
extern M2C_UNK D_00A50600;
void func_0010c2b8(s32 arg0)
{
  void *temp_s0;
  M2C_UNK *new_var;
  new_var = &D_00A50600;
  temp_s0 = new_var;
  temp_s0 = (arg0 * 0x48) + temp_s0;
  func_00109e5c(temp_s0);
  func_0010c1ec(temp_s0);
  func_0010bf4c(arg0);
}
