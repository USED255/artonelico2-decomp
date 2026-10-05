
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
M2C_UNK func_00267ac4(s32, s32);
M2C_UNK func_00268024(s32, s32);
void func_00268b38(s32 arg0)
{
  s32 var_s0;
  s32 var_s0_2;
  s32 var_s1;
  s32 var_s2;
  if (var_s2)
  {
    var_s0 = arg0 + 0xA0;
    var_s2 = 0x14;
  }
  else
  {
    var_s0 = arg0 + 0xA0;
    var_s2 = 0x14;
  }
  do
  {
    func_00267ac4(var_s0, arg0);
    var_s2 -= 1;
    var_s0 += 0x80;
  }
  while (var_s2 >= 0);
  var_s0_2 = arg0;
  var_s1 = 4;
  do
  {
    func_00268024(var_s0_2, arg0);
    var_s2 = 1;
    var_s1 -= var_s2;
    var_s0_2 += 0x20;
  }
  while (var_s1 >= 0);
}
