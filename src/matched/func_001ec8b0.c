
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
s32 baseelf_16(s32);
s32 func_001ec8b0(s32 arg0, s32 *arg1)
{
  s32 temp_a0;
  long long new_var;
  s32 temp_t6;
  s32 var_v0;
  new_var = *arg1;
  temp_t6 = new_var;
  var_v0 = 0;
  if (temp_t6 < 0xA)
  {
    *arg1 += 1;
    temp_a0 = *((s32 *) (((s8 *) ((temp_t6 << 6) + arg0)) + 0x33E0));
    if (temp_a0 != (-1))
    {
      var_v0 = baseelf_16(temp_a0);
    }
  }
  return var_v0;
}
