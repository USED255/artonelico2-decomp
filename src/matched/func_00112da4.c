
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
M2C_UNK func_0010c004(s32);
extern M2C_UNK D_00545FE0;
void func_00112da4(void)
{
  short new_var;
  s32 *temp_a0;
  s8 *var_s0;
  int var_s1;
  new_var = 4;
  var_s1 = 0;
  do
  {
    new_var = 1;
    temp_a0 = *((var_s1 * new_var) + (&D_00545FE0));
    if ((*temp_a0) != (-new_var))
    {
      var_s0 = (s8 *) temp_a0;
      do
      {
        if ((*((s8 *) (((s8 *) var_s0) + 5))) == 0x63)
        {
          func_0010c004(*((s32 *) (((s8 *) var_s0) + 0)));
        }
        var_s0 += 0xC;
      }
      while ((*((s32 *) var_s0)) != (-1));
    }
    var_s1 += 1;
  }
  while (var_s1 < 0x82U);
}
