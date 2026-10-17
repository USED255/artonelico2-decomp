
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
s32 func_001b04b0(s32);
M2C_UNK func_001b3dd0();
M2C_UNK func_001b8b24(s32, M2C_UNK);
M2C_UNK func_001d2130(s32);
extern s8 D_00BFCC4C;
void func_001d2284(s32 arg0)
{
  s32 temp_v0;
  s32 temp_v0_2;
  temp_v0_2 = func_001b04b0(3);
  temp_v0 = temp_v0_2;
  if (temp_v0 != 0)
  {
    func_001b8b24(temp_v0, 8);
  }
  if (D_00BFCC4C != 2)
  {
    func_001b3dd0();
    temp_v0_2 = func_001b04b0(arg0);
    if (temp_v0_2 != 0)
    {
      func_001b8b24(temp_v0_2, 8);
      func_001d2130(temp_v0_2);
    }
  }
}
