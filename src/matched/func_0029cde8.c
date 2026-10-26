
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
M2C_UNK func_0029c004(s32);
M2C_UNK func_0029c134(s32, M2C_UNK);
extern s8 D_00C0D11C;
void func_0029cde8(void)
{
  s32 var_s0;
  s8 *var_s1;
  s8 temp_t6;
  s8 *new_var;
  s8 new_var2;
  var_s0 = 0;
  new_var = &D_00C0D11C;
  var_s1 = new_var;
  do
  {
    func_0029c004(var_s0);
    temp_t6 = *var_s1;
    new_var2 = temp_t6;
    var_s1 += 8;
    if ((new_var2 != 2) && (temp_t6 != 3))
    {
      func_0029c134(var_s0, 2);
    }
    var_s0 += 1;
  }
  while (var_s0 < 0x3C);
}
