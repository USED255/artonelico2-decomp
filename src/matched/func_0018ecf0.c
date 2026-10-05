
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
s32 func_0018ed4c(M2C_UNK);
s32 func_0018ecf0(unsigned long arg0)
{
  int var_t5;
  int new_var;
  int new_var2;
  s32 var_v0;
  var_v0 = 0;
  if (arg0 < 3U)
  {
    var_t5 = 0;
    if (arg0 != 0)
    {
      new_var2 = 1;
      var_t5 = new_var2;
      if (arg0 != new_var2)
      {
        ;
        if (arg0 != 2)
        {
          var_t5 = ((arg0 ^ 0x15) != 0) ? (-new_var2) : (3);
        }
        else
        {
          var_t5 = 2;
        }
      }
    }
    var_v0 = func_0018ed4c(var_t5);
  }
  return var_v0;
}
