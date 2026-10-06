
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
s32 func_00102040(s32, M2C_UNK, M2C_UNK, M2C_UNK);
M2C_UNK func_002d3900(M2C_UNK);
M2C_UNK func_002d4770();
extern M2C_UNK D_009E2750;
extern s16 D_009E2756;
s32 func_001020d0(s32 arg0, M2C_UNK arg1, M2C_UNK arg2, M2C_UNK arg3)
{
  M2C_UNK *new_var2;
  s8 *new_var;
  new_var = (s8 *) (&D_009E2750);
  if ((*((s16 *) (new_var + 6))) != 0)
  {
    func_002d3900(0);
    new_var2 = &D_009E2750;
    func_002d4770();
    *((s16 *) (((s8 *) new_var2) + 6)) = 0;
  }
  do
  {
  }
  while (func_00102040(arg0, arg1, arg2, arg3) == 0);
  D_009E2756 = 1;
  return 0;
}
