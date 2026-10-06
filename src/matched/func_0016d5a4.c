
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
M2C_UNK func_0016d4d4(s16);
extern char D_00BB8018;
void func_0016d5a4(s32 arg0)
{
  M2C_UNK *new_var;
  if (arg0 >= 0)
  {
    new_var = (arg0 * 4) + (&D_00BB8018);
    func_0016d4d4(*((s16 *) (((s8 *) (*new_var)) + 0x10)));
  }
}
