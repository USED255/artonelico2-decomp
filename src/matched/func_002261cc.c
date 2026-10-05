
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
M2C_UNK func_00225e60(void *);
M2C_UNK func_002265a8(void *);
void func_002261cc(void *arg0)
{
  s16 temp_t7;
  s32 var_s0;
  if ((*((s16 *) (((s8 *) arg0) + 2))) == 1)
  {
    var_s0 = 0;
    do
    {
      func_00225e60((arg0 + (var_s0 * 0xE)) + 0x16);
      var_s0 += 1;
    }
    while (var_s0 < 8);
  }
  if ((!((*((s64 *) (((s8 *) arg0) + 0))) & 2)) && ((*((s16 *) (((s8 *) arg0) + 4))) > 0))
  {
    temp_t7 = (*((s16 *) (((s8 *) arg0) + 4)) = ((u16) (*((s16 *) (((s8 *) arg0) + 4)))) - 1);
    if (temp_t7 <= 0)
    {
      func_002265a8(arg0);
    }
  }
}
