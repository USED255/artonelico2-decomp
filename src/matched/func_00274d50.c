
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
s8 func_0018d958(s16);
s16 func_0018dcec(s16, s32);
M2C_UNK func_002748e4(void *);
M2C_UNK func_0027552c(void *, s16);
void func_00274d50(void *arg0, int arg1)
{
  s16 temp_v0;
  s32 temp_a1;
  s32 var_s1;
  s8 temp_v0_2;
  void *var_s0;
  *((s16 *) (((s8 *) arg0) + 0x6B2)) = arg1;
  var_s0 = arg0;
  var_s1 = 0;
  *((s8 *) (((s8 *) arg0) + 0x6B4)) = -1;
  do
  {
    temp_a1 = var_s1;
    var_s1 += 1;
    temp_v0 = func_0018dcec(*((s16 *) (((s8 *) arg0) + 0x6B2)), temp_a1);
    *((s16 *) (((s8 *) var_s0) + 0x632)) = temp_v0;
    *((s16 *) (((s8 *) var_s0) + 0x672)) = temp_v0;
    var_s0 += 2;
  }
  while (var_s1 < 0x20);
  temp_v0_2 = func_0018d958(*((s16 *) (((s8 *) arg0) + 0x6B2)));
  *((s8 *) (((s8 *) arg0) + 0x6B5)) = temp_v0_2;
  *((s8 *) (((s8 *) arg0) + 0x6B6)) = temp_v0_2;
  func_002748e4(arg0);
  func_0027552c(arg0 + 0xA, *((s16 *) (((s8 *) arg0) + 0x6B2)));
}
