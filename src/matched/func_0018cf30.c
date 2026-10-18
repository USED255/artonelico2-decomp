
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
M2C_UNK func_001da5e4(s16, s16);
M2C_UNK func_001da5f8(s16);
extern M2C_UNK D_00BFCC10;
void func_0018cf30(void *arg0)
{
  s16 temp_t6;
  int new_var;
  temp_t6 = *((s16 *) (((s8 *) arg0) + 6));
  switch (temp_t6)
  {
    case 2:
      func_001da5e4(*((s16 *) (((s8 *) arg0) + 8)), *((s16 *) (((s8 *) arg0) + 0xA)));
      return;

    case 1:
      new_var = 0x3C;
      if ((*((s8 *) (((s8 *) (&D_00BFCC10)) + new_var))) != 0)
    {
      func_001da5f8(*((s16 *) (((s8 *) (&D_00BFCC10)) + 0)));
      return;
    }
      return;

  }

}
