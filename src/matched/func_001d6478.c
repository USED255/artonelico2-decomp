
typedef signed char s8;
typedef char u8;
typedef short s16;
typedef unsigned short u16;
typedef int s32;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;
typedef char undefined1;
typedef unsigned short undefined2;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef char byte;
typedef char code;
typedef unsigned int uint;
typedef int s128;
typedef int u128;
typedef int s64_;
extern char *sp;
typedef s32 M2C_UNK;
typedef s8 M2C_UNK8;
typedef s16 M2C_UNK16;
typedef s32 M2C_UNK32;
typedef s64 M2C_UNK64;
extern M2C_UNK D_0079C860;
extern char D_00BB9298;
s32 func_001d6478(s32 arg0)
{
  s16 temp_t6;
  s16 temp_t6_2;
  s32 var_v0;
  void *temp_t5;
  var_v0 = 0;
  loop_1:
  temp_t5 = (var_v0 * 8) + ((char *) (&D_0079C860));

  if ((((*((s16 *) (((s8 *) temp_t5) + 0))) != arg0) || (((temp_t6 = *((s16 *) (((s8 *) temp_t5) + 2)), temp_t6 >= 0)) && ((temp_t6 == (-1)) || ((*((temp_t6 * 4) + (&D_00BB9298))) == 0)))) || ((((temp_t6_2 = *((s16 *) (((s8 *) temp_t5) + 4)), temp_t6_2 >= 0)) && (temp_t6_2 != (-1))) && ((*((temp_t6_2 * 4) + (&D_00BB9298))) != 0)))
  {
    var_v0 += 1;
    if (var_v0 >= 0xE)
    {
      var_v0 = -1;
    }
    else
    {
      goto loop_1;
    }
  }
  return var_v0;
}
