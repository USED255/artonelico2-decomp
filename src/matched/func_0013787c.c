
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
M2C_UNK func_00105f6c();
M2C_UNK func_00136ba4(void *);
s32 func_001377d4(s32);
extern M2C_UNK D_00AF0850;
s32 func_0013787c(void *arg0)
{
  s32 var_s2;
  M2C_UNK *new_var;
  s32 var_v0;
  var_v0 = -1;
  var_s2 = 0;
  new_var = &D_00AF0850;
  if ((*((s32 *) (((s8 *) (&D_00AF0850)) + 0))) >= 0)
  {
    if ((*((s32 *) (((s8 *) new_var) + 0))) != (*((s32 *) (((s8 *) new_var) + 8))))
    {
      if ((*((s32 *) (((s8 *) arg0) + 0x30))) != 0)
      {
        func_00105f6c();
      }
      var_s2 = func_001377d4(*((s32 *) (((s8 *) new_var) + 0)));
    }
    func_00136ba4(arg0);
    var_v0 = var_s2;
  }
  return var_v0;
}
