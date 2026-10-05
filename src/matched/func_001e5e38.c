
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
void *baseelf_14();
extern s32 D_007AF2D0;
void *func_001e5e38(s32 *arg0)
{
  s32 temp_t5;
  void *temp_t6;
  void *var_v0;
  temp_t6 = D_007AF2D0 + 0x212E0;
  temp_t5 = *arg0;
  if (temp_t5 == (*((s16 *) (((s8 *) temp_t6) + 0x3FC64))))
  {
    *arg0 = temp_t5 + 1;
    return baseelf_14();
  }
  var_v0 = 0;
  if (temp_t5 < (*((s16 *) (((s8 *) temp_t6) + 0x3FC64))))
  {
    *arg0 += 1;
    if ((*((s16 *) (((s8 *) ((temp_t5 * 0x38B0) + temp_t6)) + 0x1C))) >= 0)
    {
      if (temp_t6 || temp_t5)
      {
        var_v0 = temp_t6 + (temp_t5 * 0x38B0);
      }
      else
      {
        var_v0 = temp_t6 + (temp_t5 * 0x38B0);
      }
    }
  }
  return var_v0;
}
