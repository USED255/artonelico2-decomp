
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
u8 *func_001928a8();
extern char D_00778238;
s32 func_001928d8(void)
{
  int new_var;
  u32 var_t6;
  s32 new_var2;
  u8 *var_v0;
  u8 var_t7;
  var_v0 = func_001928a8();
  new_var = -4;
  var_t7 = *var_v0;
  var_t6 = 0;
  loop_1:
  var_v0 += 1;

  if (var_t7 != 0)
  {
    var_t7 = *var_v0;
    var_t6 += 1;
    goto loop_1;
  }
  new_var2 = *((s32 *) (((s8 *) (((((s32) (var_t6 + (var_t6 >> 0x1F))) >> 1) * 4) + (&D_00778238))) + new_var));
  return new_var2;
}
