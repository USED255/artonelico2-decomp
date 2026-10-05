
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
M2C_UNK func_00200f78(s32);
extern s32 D_007AF2D0;
void baseelf_110(void)
{
  long long new_var;
  s32 temp_s1;
  s32 var_s0;
  temp_s1 = D_007AF2D0 + 0x212E0;
  var_s0 = 0;
  do
  {
    func_00200f78((temp_s1 + (var_s0 * 0x1730)) + 0x3FCA0);
    new_var = ((var_s0 * 2) + temp_s1) + 0x3FC80;
    *((s16 *) (((s8 *) new_var) + 0xE)) = -1;
    var_s0 += 1;
  }
  while (var_s0 < 2);
}
