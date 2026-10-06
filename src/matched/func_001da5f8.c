
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
M2C_UNK func_00102878(M2C_UNK *);
M2C_UNK **func_00103b5c(s16);
extern char D_007A0A00;
extern M2C_UNK D_0096C2B8;
extern M2C_UNK D_0096C2C8;
void func_001da5f8(u32 arg0)
{
  M2C_UNK *new_var;
  if (arg0 < 0x223U)
  {
    new_var = (arg0 * 0x34) + (&D_007A0A00);
    func_00102878(*func_00103b5c(*((s16 *) (((s8 *) new_var) - -0x24))));
    func_00102878(&D_0096C2B8);
    func_00102878(&D_0096C2C8);
  }
}
