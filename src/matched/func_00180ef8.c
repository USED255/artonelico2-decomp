
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
extern s32 D_0061D4C0;
s32 func_00180ef8(s32 arg0)
{
  s32 var_v0;
  int new_var4;
  void *new_var2;
  s8 *new_var;
  s64 temp_t6;
  unsigned int new_var3;
  void *temp_t5;
  temp_t5 = D_0061D4C0 + (arg0 * 0x470);
  new_var4 = 1;
  new_var2 = temp_t5;
  temp_t6 = *((s64 *) (((s8 *) new_var2) + 0x460));
  new_var3 = 0;
  var_v0 = new_var3;
  if (temp_t6 & new_var4)
  {
    var_v0 = new_var4;
    new_var = ((s8 *) new_var2) + 0x460;
    *((s64 *) new_var) = (s64) (temp_t6 & (~new_var4));
  }
  return var_v0;
}
