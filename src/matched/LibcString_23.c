
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
s8 *LibcString_23(s8 *arg0, s8 *arg1)
{
  s32 var_t4;
  s8 *var_v0;
  s8 temp_t5;
  s8 new_var2;
  s8 *new_var;
  var_v0 = arg0;
  temp_t5 = (*arg0) == 0;
  if (temp_t5)
  {
    return ((*arg1) != 0) ? (0) : (var_v0);
  }
  loop_2:
  var_t4 = 0;

  loop_3:
  temp_t5 = *(arg1 + var_t4);

  if (temp_t5 != 0)
  {
    new_var2 = *(new_var = var_v0 + var_t4);
    var_t4 += 1;
    if (temp_t5 != new_var2)
    {
      var_v0 += 1;
      if ((*var_v0) == 0)
      {
        var_v0 = 0;
      }
      else
      {
        goto loop_2;
      }
    }
    else
    {
      goto loop_3;
    }
  }
  return var_v0;
}
