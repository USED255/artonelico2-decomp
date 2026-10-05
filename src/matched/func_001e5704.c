
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
M2C_UNK baseelf_26(void *, s32, M2C_UNK);
extern s32 D_007AF2D0;
void func_001e5704(s32 arg0, M2C_UNK arg1)
{
  s32 var_a0;
  s32 var_s0;
  void *temp_s1;
  temp_s1 = D_007AF2D0 + 0x212E0;
  var_s0 = 0;
  if ((*((s16 *) (((s8 *) temp_s1) + 0x3FC64))) > 0)
  {
    var_a0 = 0 * 0x38B0;
    do
    {
      var_a0 = var_s0 * 0x38B0;
      baseelf_26(temp_s1 + var_a0, arg0, arg1);
      var_s0 += 1;
    }
    while (var_s0 < (*((s16 *) (((s8 *) temp_s1) + 0x3FC64))));
  }
}
