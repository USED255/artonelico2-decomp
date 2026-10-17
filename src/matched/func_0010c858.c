
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
M2C_UNK func_0010c004(s32);
extern s32 D_009DFC20;
extern M2C_UNK D_00A50600;
void func_0010c858(void)
{
  s16 temp_t6;
  s32 var_s0;
  unsigned int new_var;
  var_s0 = 0xA;
  do
  {
    new_var = 0x2C;
    temp_t6 = *((s16 *) (((s8 *) (((u8 *) (&D_00A50600) + var_s0 * 0x48))) + new_var));
    if ((temp_t6 >= 0) && (temp_t6 < (D_009DFC20 << 5)))
    {
      func_0010c004(var_s0);
    }
    var_s0 += 1;
  }
  while (var_s0 < 0x1DE8);
}
