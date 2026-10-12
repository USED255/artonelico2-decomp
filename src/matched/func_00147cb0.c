
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
extern s8 D_00586E50;
extern M2C_UNK D_00AF2350;
void func_00147cb0(void)
{
  s32 var_t5;
  s8 *new_var;
  s8 *temp_t6;
  var_t5 = 0;
  D_00586E50 = 0;
  do
  {
    new_var = &D_00AF2350;
    temp_t6 = (var_t5 * 0x18) + new_var;
    new_var = temp_t6;
    var_t5 += 1;
    *new_var = 0;
  }
  while (var_t5 < 0xC);
}
