
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
M2C_UNK func_0018e8f8(M2C_UNK);
void func_0018e898(unsigned long long arg0)
{
  M2C_UNK var_t5;
  int new_var;
  if (arg0 >= 3U)
  {
    return;
  }
  var_t5 = 0;
  if (arg0 != 0)
  {
    var_t5 = 1;
    new_var = 1;
    if (arg0 != new_var)
    {
      if (arg0 != 2)
      {
        var_t5 = ((arg0 ^ 0x15) != 0) ? (-new_var) : (3);
      }
      else
      {
        var_t5 = 2;
      }
    }
  }
  func_0018e8f8(var_t5);
}
