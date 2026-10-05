
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
void func_0011eddc(void *arg0, s32 arg1)
{
  s32 var_a1;
  void *var_a0;
  int new_var;
  var_a0 = arg0;
  var_a1 = arg1;
  new_var = -1;
  if (var_a1 > 0)
  {
    do
    {
      *((s16 *) (((s8 *) var_a0) + 0)) = 0;
      *((s16 *) (((s8 *) var_a0) + 2)) = new_var;
      var_a1 -= 1;
      var_a0 += 8;
    }
    while (var_a1 != 0);
  }
}
