
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
s32 func_0018f610(s16);
s32 func_00244294(s16);
M2C_UNK func_002448e0(s16);
M2C_UNK func_00244d70(s16);
s16 func_00245608(s16);
M2C_UNK func_0024a93c(void *);
M2C_UNK func_0024aa1c(void *, s16);
void func_00243894(void *arg0)
{
  s16 temp_t5;
  unsigned long long temp_t6;
  s16 var_a0;
  void *temp_s0;
  temp_t5 = *((s16 *) (((s8 *) arg0) + 0xD92));
  if (temp_t5 == (-1))
  {
    temp_t6 = *((s16 *) (((s8 *) arg0) + 0xD90));
    var_a0 = 0;
    if (temp_t6 != 0)
    {
      var_a0 = 1;
      if (temp_t6 != 1)
      {
        if (temp_t6 != 2)
        {
          var_a0 = ((temp_t6 ^ 3) != 0) ? (temp_t5) : (0x15);
        }
        else
        {
          var_a0 = 2;
        }
      }
    }
    if ((func_0018f610(var_a0) != 0) && (func_00244294(*((s16 *) (((s8 *) arg0) + 0xD90))) != 0))
    {
      func_002448e0(*((s16 *) (((s8 *) arg0) + 0xD90)));
    }
  }
  else
  {
    func_00244d70(*((s16 *) (((s8 *) arg0) + 0xD90)));
  }
  temp_s0 = arg0 + 0xF90;
  *((s16 *) (((s8 *) arg0) + 0x1702)) = func_00245608(*((s16 *) (((s8 *) arg0) + 0xD90)));
  func_0024a93c(temp_s0);
  func_0024aa1c(temp_s0, *((s16 *) (((s8 *) arg0) + 0xD90)));
}
