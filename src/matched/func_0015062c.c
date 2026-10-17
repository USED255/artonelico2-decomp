
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
extern s32 D_0058B298;
extern M2C_UNK D_00BB5BE8;
s32 func_0015062c(void)
{
  short new_var;
  s32 temp_t7;
  s32 var_t3;
  var_t3 = 0;
  loop_1:
  temp_t7 = D_0058B298 + 1;

  new_var = *(M2C_UNK *) ((u8 *) (&D_00BB5BE8) + D_0058B298 * 0x38);
  if (new_var >= 0)
  {
    var_t3 += 1;
    D_0058B298 = (temp_t7 >= 0x64) ? (0) : (temp_t7);
    if (var_t3 < 0x64)
    {
      goto loop_1;
    }
  }
  return D_0058B298;
}
