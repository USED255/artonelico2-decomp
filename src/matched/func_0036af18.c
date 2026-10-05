
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
s32 func_0036af18(s32 *arg0, void *arg1, s32 *arg2)
{
  s32 var_t4;
  s32 var_t5;
  s32 var_t7;
  s32 var_v0;
  s8 temp_t6;
  s8 temp_t7;
  temp_t6 = *((s8 *) (((s8 *) arg1) + 0));
  switch (temp_t6)
  {
    case 0x61:
      var_v0 = 0x108;
      var_t4 = 1;
      var_t5 = 0x208;
      block_8:
    temp_t7 = *((s8 *) (((s8 *) arg1) + 1));

      if (temp_t7 != 0)
    {
      if ((temp_t7 == 0x2B) || ((var_t7 = var_t4 | var_t5, (*((s8 *) (((s8 *) arg1) + 2))) == 0x2B)))
      {
        var_v0 = 0x10;
        var_t4 = 2;
        goto block_12;
      }
    }
    else
    {
      block_12:
      ;

    }
      *arg2 = var_t4 | var_t5;
      return var_v0;

    default:
      *arg0 = 0x16;
      return 0;

    case 0x77:
      var_v0 = 8;
      var_t4 = 1;
      var_t5 = 0x600;
      goto block_8;

    case 0x72:
      var_v0 = 4;
      var_t4 = 0;
      var_t5 = 0;
      goto block_8;

  }

}
