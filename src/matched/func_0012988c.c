
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
s32 func_0012988c(void *arg0, s32 arg1, s32 arg2)
{
  s32 temp_t6;
  s32 var_t2;
  s32 var_t3;
  s32 var_v0;
  void *temp_t4;
  var_t2 = 0;
  var_t3 = 0;
  var_v0 = 0;
  if (arg2 > 0)
  {
    loop_2:
    temp_t6 = var_t3 * 0xA;

    temp_t4 = (arg1 * 0x14) + (*((s32 *) (((s8 *) arg0) + 8)));
    var_t3 += 1;
    var_t2 += *((u16 *) (((s8 *) (temp_t6 + (*((s32 *) (((s8 *) temp_t4) + 4))))) + 2));
    var_v0 = var_t3;
    if (var_v0 < arg2)
    {
      if (var_t3 < ((s32) (*((u8 *) (((s8 *) temp_t4) + 0)))))
      {
        goto loop_2;
      }
    }
    var_v0 = var_t2;
  }
  return var_v0;
}
