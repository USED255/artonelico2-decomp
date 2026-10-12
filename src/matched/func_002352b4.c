
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
M2C_UNK LibcString_8(s8 *, M2C_UNK, M2C_UNK);
M2C_UNK func_002354c4(M2C_UNK);
extern unsigned char D_007DBCF8;
extern s8 D_00BFEAA8;
void func_002352b4(void)
{
  s32 temp_t5;
  s32 var_t4;
  unsigned char *new_var;
  s8 *temp_t5_2;
  u16 temp_t6;
  LibcString_8(&D_00BFEAA8, 0, 0x7D4);
  D_00BFEAA8 = 0;
  var_t4 = 0;
  do
  {
    temp_t5 = var_t4 * 0x14;
    new_var = &D_007DBCF8;
    temp_t6 = *((u16 *) (((s8 *) ((var_t4 * 0x10) + new_var)) + 0xA));
    var_t4 += 1;
    temp_t5_2 = &(&D_00BFEAA8)[temp_t5];
    *((u16 *) (((s8 *) temp_t5_2) + 0x10)) = temp_t6;
    *((s8 *) (((s8 *) temp_t5_2) + 4)) = 0;
  }
  while (var_t4 < 0x64);
  func_002354c4(1);
}
