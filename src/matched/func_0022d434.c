
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
M2C_UNK baseelf_70(void *, s32, M2C_UNK);
M2C_UNK func_0014c0c8(M2C_UNK);
s32 func_001e594c(s16);
s32 func_001eb354(void *, M2C_UNK);
s32 func_00233d40(s32, M2C_UNK, M2C_UNK);
void func_0022d434(void *arg0, void *arg1, s32 arg2)
{
  s32 temp_s0;
  s32 temp_t7;
  s32 temp_v0;
  s32 var_s0;
  s32 var_s1;
  var_s1 = 0;
  do
  {
    if (arg1 == (*((s32 *) (((s8 *) ((var_s1 * 4) + arg0)) + 0x54))))
    {
      temp_t7 = (-(*((s32 *) (((s8 *) arg0) + 0xA4)))) * arg2;
      temp_s0 = (s32) ((temp_t7 >= 0) ? (temp_t7) : (temp_t7 + 3));
      temp_s0 = temp_s0 >> 2;
      var_s0 = (temp_s0 / func_001eb354(arg1, 2)) * 0x64;
      temp_v0 = func_001e594c(*((s16 *) (((s8 *) arg1) + 0x14A)));
      if (temp_v0 != 0)
      {
        var_s0 -= ((s32) (var_s0 * func_00233d40(temp_v0, 0x25, 0))) / 100;
      }
      func_0014c0c8(0x118);
      baseelf_70(arg0, var_s0, 0);
    }
    var_s1 += 1;
  }
  while (var_s1 < 2);
}
