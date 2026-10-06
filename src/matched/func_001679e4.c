
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
void func_001679e4(void *arg0)
{
  s32 temp_a0;
  int new_var;
  s32 var_s1;
  if ((*((s32 *) (((s8 *) arg0) + 8))) != 0)
  {
    var_s1 = 0;
    if ((*((s32 *) (((s8 *) arg0) + 0))) > 0)
    {
      new_var = 0;
      do
      {
        temp_a0 = (*((s32 *) (((s8 *) arg0) + 8))) + (var_s1 * 0x50);
        var_s1 += 1;
        func_001678a4(temp_a0);
      }
      while (var_s1 < (*((s32 *) (((s8 *) arg0) + new_var))));
    }
    baseelf_104(*((s32 *) (((s8 *) arg0) + 8)));
  }
  *((s32 *) (((s8 *) arg0) + new_var)) = 0;
  *((s32 *) (((s8 *) arg0) + 8)) = 0;
}
