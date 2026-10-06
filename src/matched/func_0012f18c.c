
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
M2C_UNK func_0012f1e0(s32, void *, M2C_UNK);
void func_0012f18c(s32 arg0, void *arg1)
{
  void *var_a1;
  s32 new_var;
  void *var_s0;
  new_var = *((s32 *) (((s8 *) arg1) + 0xD0));
  var_s0 = arg1;
  if (new_var >= 0)
  {
    var_a1 = var_s0;
    do
    {
      func_0012f1e0(arg0, var_a1, 0);
      var_s0 += 0xF0;
      var_a1 = var_s0;
    }
    while ((*((s32 *) (((s8 *) var_s0) + 0xD0))) >= 0);
  }
}
