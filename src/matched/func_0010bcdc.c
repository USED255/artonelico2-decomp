
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
M2C_UNK LibcString_8(M2C_UNK *, M2C_UNK, M2C_UNK);
s32 baseelf_98(M2C_UNK, M2C_UNK);
extern M2C_UNK D_00A50600;
void func_0010bcdc(void)
{
  void *new_var;
  s32 var_s2;
  s32 var_t4;
  void *temp_s0;
  void *temp_t6;
  void *temp_t6_2;
  LibcString_8(&D_00A50600, 0, 0x86940);
  var_t4 = 0;
  do
  {
    temp_t6 = (M2C_UNK *) ((u8 *) (&D_00A50600) + var_t4 * 0x48);
    var_t4 += 1;
    temp_t6_2 = temp_t6 + 0x20;
    *((s16 *) (((s8 *) temp_t6_2) + 0xC)) = -1;
    *((s16 *) (((s8 *) temp_t6_2) + 0xE)) = -1;
  }
  while (var_t4 < 0x1DE8);
  var_s2 = 0;
  do
  {
    temp_s0 = (M2C_UNK *) ((u8 *) (&D_00A50600) + var_s2 * 0x48);
    var_s2 += 1;
    *((s32 *) (((s8 *) temp_s0) + 0x20)) = baseelf_98(0x10, 0x60);
    new_var = temp_s0 + 0x20;
    *((s32 *) (((s8 *) new_var) + 4)) = baseelf_98(0x10, 0x60);
  }
  while (var_s2 < 0xA);
}
