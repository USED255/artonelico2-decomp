
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
M2C_UNK func_00204028(s32, s32);
void func_001e820c(s32 arg0, s32 arg1)
{
  s32 var_a1;
  s32 var_s0;
  var_s0 = 0;
  var_a1 = 0 << 5;
  do
  {
    var_a1 = var_s0 << 5;
    func_00204028(arg0, (arg1 + var_a1) + 0x121A0);
    var_s0 += 1;
  }
  while ((unsigned int) (var_s0 < 0xA));
}
