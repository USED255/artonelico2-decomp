
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
M2C_UNK func_0014e980(M2C_UNK);
M2C_UNK func_0014ec3c(s16);
extern M2C_UNK D_005896E0;
extern M2C_UNK D_009E5340;
void func_0014ec64(s32 arg0)
{
  M2C_UNK *new_var2;
  s16 temp_s0;
  int new_var;
  temp_s0 = *((M2C_UNK *) ((s8 *) (&D_005896E0) + arg0 * 2));
  new_var2 = &D_009E5340;
  new_var = (*((M2C_UNK *) ((s8 *) new_var2 + temp_s0 * 0x28))) != arg0;
  if (new_var)
  {
    return;
  }
  if (temp_s0 == 0)
  {
    if ((*((s32 *) (((s8 *) new_var2) + 0x28))) >= 0)
    {
      func_0014e980(1);
    }
  }
  func_0014ec3c(temp_s0);
}
