
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
extern unsigned char D_00BB8578;
void func_0018d7e8(s32 arg0, s32 arg1)
{
  s32 *temp_a0;
  s32 temp_t7;
  s32 var_t6;
  temp_a0 = (arg0 * 0x78) + (&D_00BB8578);
  temp_t7 = (*temp_a0) + arg1;
  *temp_a0 = temp_t7;
  var_t6 = temp_t7;
  if (temp_t7 >= 0)
  {
    if (var_t6 > 0xF4240)
    {
      var_t6 = 0xF4240;
    }
  }
  else
  {
    var_t6 = 0;
  }
  *temp_a0 = var_t6;
}
