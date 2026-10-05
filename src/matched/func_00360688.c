
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
s32 func_00360688(unsigned int arg0, s32 (*arg1)(void *))
{
  s32 var_s1;
  s32 var_s3;
  int new_var;
  void *var_s0;
  void *var_s2;
  var_s2 = arg0 + 0x1D8;
  var_s3 = 0;
  if (var_s2 != 0)
  {
    do
    {
      var_s1 = *((s32 *) (((s8 *) var_s2) + 4));
      var_s1 = var_s1 - 1;
      new_var = 0;
      var_s0 = *((void **) (((s8 *) var_s2) + 8));
      if (var_s1 >= new_var)
      {
        do
        {
          if ((*((s16 *) (((s8 *) var_s0) + 0xC))) != new_var)
          {
            var_s3 |= arg1(var_s0);
          }
          var_s1 -= 1;
          var_s0 += (unsigned long long) 0x58;
        }
        while (var_s1 >= new_var);
      }
      var_s2 = *((void **) (((s8 *) var_s2) + new_var));
    }
    while (var_s2 != 0);
  }
  return var_s3;
}
