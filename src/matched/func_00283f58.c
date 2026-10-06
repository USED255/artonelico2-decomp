
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
M2C_UNK func_0027a9f4(s32, void *);
M2C_UNK func_0027afb8(s32);
extern M2C_UNK D_007FEEA0;
void func_00283f58(void *arg0)
{
  s32 temp_s0;
  s32 temp_s0_2;
  s32 var_s1;
  void *temp_a1;
  M2C_UNK *new_var;
  var_s1 = 0;
  do
  {
    new_var = &D_007FEEA0;
    temp_a1 = new_var;
    temp_a1 = (var_s1 * 4) + temp_a1;
    temp_s0 = arg0 + (var_s1 * 0x50);
    var_s1 += 1;
    temp_s0_2 = temp_s0 + 0xA60;
    func_0027a9f4(temp_s0_2, temp_a1);
    func_0027afb8(temp_s0 + 0xA60);
  }
  while (var_s1 < 8);
  *((s8 *) (((s8 *) arg0) + 0xD03)) = 0x14;
}
