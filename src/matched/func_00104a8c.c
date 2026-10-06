
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
s32 func_00103b78();
s32 func_001049f0(s32);
extern M2C_UNK D_00A38A88;
u32 func_00104a8c(void)
{
  s32 temp_v0;
  s8 *new_var;
  u32 var_t7;
  temp_v0 = func_001049f0(func_00103b78());
  var_t7 = 0;
  if (temp_v0 >= 0)
  {
    var_t7 = ((u32) (~(*((s16 *) (new_var = ((s8 *) ((temp_v0 * 0x18) + (new_var = &D_00A38A88))) + 0xA))))) >> 0x1F;
  }
  return var_t7;
}
