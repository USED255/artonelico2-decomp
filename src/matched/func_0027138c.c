
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
M2C_UNK baseelf_153(s32, M2C_UNK *, s16, s16);
M2C_UNK func_0011299c(u8);
M2C_UNK func_0011e440(M2C_UNK *, M2C_UNK, M2C_UNK, M2C_UNK);
M2C_UNK func_0011e468(M2C_UNK *, M2C_UNK);
M2C_UNK func_0013e2fc(void *);
extern M2C_UNK D_003B98B8;
extern s32 D_009DFCE0;
void func_0027138c(s32 arg0, void *arg1)
{
  u8 temp_s0;
  s8 *new_var2;
  s32 *new_var;
  func_0013e2fc(arg1);
  temp_s0 = *((u8 *) (((s8 *) arg1) + 0));
  if (temp_s0 == 0)
  {
    return;
  }
  if ((*((s8 *) (((s8 *) arg1) + 0xA))) == 0)
  {
    func_0011e468(&D_003B98B8, 0);
  }
  else
  {
    func_0011e440(&D_003B98B8, 0, 2, -1);
  }
  new_var2 = (s8 *) (&D_003B98B8);
  new_var = (s32 *) (((s8 *) (&D_003B98B8)) + 0x100);
  *new_var = (s32) D_009DFCE0;
  *((s32 *) (new_var2 + 0x130)) = (s32) D_009DFCE0;
  func_0011299c(temp_s0);
  baseelf_153(arg0, &D_003B98B8, *((s16 *) (((s8 *) arg1) + 6)), *((s16 *) (((s8 *) arg1) + 8)));
  func_0011299c(0x80U);
}
