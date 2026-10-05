
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
M2C_UNK baseelf_104(s32);
M2C_UNK func_001678a4(s32);
M2C_UNK func_001a52c4(void *);
M2C_UNK func_001a720c();
M2C_UNK func_001b5984(s16);
extern s8 D_00BFCC4C;
void func_001a523c(void *arg0)
{
  s32 temp_t7;
  s32 temp_t7_2;
  s8 *new_var2;
  s8 new_var;
  if (temp_t7)
  {
    new_var = D_00BFCC4C;
  }
  else
  {
    new_var = D_00BFCC4C;
  }
  if (new_var != 2)
  {
    func_001b5984(*((s16 *) (((s8 *) arg0) + 0)));
  }
  func_001a52c4(arg0);
  temp_t7 = *((s32 *) (((s8 *) arg0) + 4));
  if (1)
  {
    if (temp_t7 != 0)
    {
      func_001678a4(temp_t7);
      baseelf_104(*((s32 *) (((s8 *) arg0) + 4)));
      new_var2 = (s8 *) arg0;
      *((s32 *) (new_var2 + 4)) = 0;
    }
    temp_t7_2 = *((s32 *) (((s8 *) arg0) + 8));
    if (temp_t7_2 != 0)
    {
      func_001678a4(*((s32 *) (((s8 *) arg0) + 8)));
      baseelf_104(*((s32 *) (((s8 *) arg0) + 8)));
      *((s32 *) (((s8 *) arg0) + 8)) = 0;
    }
  }
  *((s16 *) (((s8 *) arg0) + 0)) = -1;
  func_001a720c();
}
