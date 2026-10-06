
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
s32 func_001a1d9c();
extern char D_007EB828;
s16 func_0024c830(void)
{
  s16 var_t3;
  s32 temp_v0;
  s32 var_t4;
  void *temp_t6;
  temp_v0 = func_001a1d9c();
  var_t3 = 0x4B;
  var_t4 = 0;
  loop_1:
  temp_t6 = (var_t4 * 0xC) + (&D_007EB828);

  var_t4 += 1;
  if ((*((s16 *) (((s8 *) temp_t6) + 0))) == temp_v0)
  {
    var_t3 = *((s16 *) (((s8 *) temp_t6) + 2));
  }
  else
    if (var_t4 >= 3)
  {
  }
  else
  {
    goto loop_1;
  }
  if ((temp_v0 == 0x26) || (temp_v0 == 0x28))
  {
    var_t3 = 0x4F;
  }
  return var_t3;
}
