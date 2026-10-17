
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
M2C_UNK func_00145264(void *, s32, s8);
s16 func_0027dbbc();
void func_0027e4a4(void *arg0)
{
  s16 temp_v0;
  s32 temp_a1;
  s32 var_s1;
  s8 *var_s0;
  temp_v0 = (*((s16 *) (((s8 *) arg0) + 0x1FC2)) = func_0027dbbc());
  if (temp_v0 > 0)
  {
    var_s1 = 0;
    var_s0 = arg0 + 0x1FC8;
    do
    {
      temp_a1 = var_s1;
      var_s1 += 1;
      func_00145264(arg0, temp_a1, *var_s0);
      var_s0 += 1;
    }
    while (var_s1 < (*((s16 *) (((s8 *) arg0) + 0x1FC2))));
  }
}
