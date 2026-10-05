
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
M2C_UNK func_002206a0();
M2C_UNK func_002206bc(s32);
M2C_UNK func_00220714(s32);
void func_00220648(s32 arg0)
{
  s32 var_a0;
  s32 var_s0;
  func_002206a0();
  var_s0 = 0;
  var_a0 = 0 << 6;
  do
  {
    var_a0 = var_s0 << 6;
    func_002206bc((arg0 + var_a0) + 0xA0);
    var_s0 += 1;
  }
  while (var_s0 < 0x64);
  func_00220714(arg0);
}
