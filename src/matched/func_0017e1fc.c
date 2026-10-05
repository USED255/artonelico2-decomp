
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
s32 func_0017e18c();
s32 func_0017e1fc(void *arg0, s32 arg1)
{
  s16 temp_t7;
  s32 temp_t5;
  s32 temp_t7_2;
  s32 var_t4;
  s32 var_v0;
  void *var_a0;
  var_v0 = func_0017e18c();
  temp_t5 = var_v0;
  var_t4 = 0;
  if (arg1 > 0)
  {
    var_a0 = arg0;
    loop_2:
    temp_t7 = *((s16 *) (((s8 *) var_a0) + 4));

    if (temp_t7 >= 0)
    {
      var_v0 = 0;
      if (temp_t5 >= temp_t7)
      {
        var_v0 = 1;
        if ((temp_t7 != temp_t5) && (((temp_t7_2 = var_t4 < (arg1 - 1), var_t4 += 1, temp_t7_2 == 0)) || (temp_t5 >= (*((s16 *) (((s8 *) var_a0) + 0xC))))))
        {
          var_a0 += 8;
          if (var_t4 >= arg1)
          {
            goto block_8;
          }
          goto loop_2;
        }
      }
    }
    else
    {
      goto block_8;
    }
  }
  else
  {
    block_8:
    var_v0 = 0;

  }
  return var_v0;
}
