
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
s32 baseelf_98(M2C_UNK, M2C_UNK);
M2C_UNK func_001bad2c(s32, s32, M2C_UNK);
extern M2C_UNK D_00BC6790;
s32 func_001b118c(s32 arg0, M2C_UNK arg1)
{
  s32 temp_t7;
  s32 temp_v0;
  s8 *new_var;
  s32 var_t5;
  s32 var_v0;
  void *temp_s0;
  var_t5 = 0;
  loop_1:
  temp_t7 = var_t5 * 4;

  var_t5 += 1;
  new_var = &D_00BC6790;
  temp_s0 = (temp_t7 + new_var) + 0x70;
  if ((*((s32 *) (((s8 *) temp_s0) + 8))) == 0)
  {
    temp_v0 = baseelf_98(0x10, 0xD0);
    *((u32 *) (((s8 *) temp_s0) + 8)) = temp_v0;
    func_001bad2c(temp_v0, arg0, arg1);
    new_var = (s8 *) temp_s0;
    var_v0 = *((s32 *) (new_var + 8));
  }
  else
    if (var_t5 >= 0x800)
  {
    var_v0 = 0;
  }
  else
  {
    goto loop_1;
  }
  return var_v0;
}
