
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
void *func_0029a2b4(s32);
s16 func_0029a45c(s32 arg0)
{
  s16 *new_var;
  s16 var_v0;
  s32 var_s0;
  s8 *new_var2;
  void *temp_v0;
  var_s0 = 0;
  loop_1:
  temp_v0 = func_0029a2b4(var_s0);

  new_var2 = (s8 *) temp_v0;
  new_var = (s16 *) (((s8 *) temp_v0) + 8);
  var_s0 += 1;
  if ((*((s16 *) (new_var2 + 0))) == arg0)
  {
    var_v0 = *new_var;
  }
  else
  {
    if (var_s0 >= 8)
    {
    }
    else
    {
      goto loop_1;
    }
    var_v0 = 0;
  }
  return var_v0;
}
