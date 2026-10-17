
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
M2C_UNK func_00109e5c(void *, s32);
M2C_UNK func_0010a4c0(s32, s8, s8, u8);
M2C_UNK func_0010bf4c(s32);
M2C_UNK func_0010c2b8(s32, s32);
extern M2C_UNK D_00545FE0;
extern M2C_UNK D_00A50600;
void func_00112c4c(void)
{
  s32 *temp_a0;
  s8 *var_s0;
  s32 temp_a0_2;
  u32 var_s1;
  var_s1 = 0;
  do
  {
    temp_a0 = *((s32 **) ((s8 *) &D_00545FE0 + var_s1 * 4));
    if ((*temp_a0) != (-1))
    {
      var_s0 = (s8 *) temp_a0;
      do
      {
        ;
        if ((*((s8 *) (((s8 *) var_s0) + 5))) != 0x63)
        {
          func_0010c2b8(*((s32 *) (((s8 *) var_s0) + 0)), *((s32 *) (((s8 *) var_s0) + 8)));
          func_0010a4c0(*((s32 *) (((s8 *) var_s0) + 0)), *((s8 *) (((s8 *) var_s0) + 5)), *((s8 *) (((s8 *) var_s0) + 6)), *((u8 *) (((s8 *) var_s0) + 7)));
          func_0010bf4c(*((s32 *) (((s8 *) var_s0) + 0)));
        }
        else
        {
          func_00109e5c((void *) ((s8 *) &D_00A50600 + (*((s32 *) (((s8 *) var_s0) + 0))) * 0x48), *((s32 *) (((s8 *) var_s0) + 8)));
        }
        var_s0 += 0xC;
      }
      while ((*((s32 *) var_s0)) != (-1));
    }
    var_s1 += 1;
  }
  while (var_s1 < 0x82U);
}
