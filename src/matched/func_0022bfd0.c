
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
M2C_UNK baseelf_153(M2C_UNK *, M2C_UNK *, s32, s32);
M2C_UNK func_0010dee8(M2C_UNK *, M2C_UNK, M2C_UNK, M2C_UNK);
M2C_UNK func_0022b0f4(M2C_UNK *, s32, s32, s32);
M2C_UNK func_0022b320(s32, s32, s32);
M2C_UNK func_0022bafc(M2C_UNK *, s32, s32, s32);
extern M2C_UNK D_00463558;
extern M2C_UNK D_00A504E0;
void func_0022bfd0(s32 arg0, s32 arg1, s32 arg2)
{
  s32 var_a1;
  M2C_UNK *new_var;
  s32 var_s0;
  new_var = &D_00A504E0;
  baseelf_153(new_var, &D_00463558, arg1 + 0xA4, arg2 + 0x166);
  func_0022b320(arg0, arg1, arg2);
  func_0022b0f4(new_var, arg0 + 0x1C, arg1, arg2);
  func_0010dee8(new_var, 0, 3, 0x80);
  var_a1 = arg0 + 0x44;
  func_0022b0f4(new_var, var_a1, arg1, arg2);
  func_0010dee8(new_var, 0, 1, 0x80);
  var_s0 = 0;
  var_a1 = 0 * 8;
  do
  {
    var_a1 = var_s0 * 8;
    func_0022bafc(new_var, (arg0 + var_a1) + 0x6C, arg1, arg2);
    var_s0 += 1;
  }
  while (var_s0 < 2);
}
