
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
void func_0010ccb8(s32);
M2C_UNK func_002b5b68(M2C_UNK);
extern unsigned char D_00A50600;
s32 func_0010cd64(void)
{
  s32 var_s0;
  s32 var_s1;
  void *temp_t6;
  var_s0 = 0;
  var_s1 = 0;
  do
  {
    temp_t6 = (var_s0 * 0x48) + (&D_00A50600);
    if (((*((s16 *) (((s8 *) temp_t6) + 0x2C))) >= 0) || ((*((s16 *) (((s8 *) temp_t6) + 0x2E))) >= 0))
    {
      var_s1 += 1;
      func_0010ccb8(var_s0);
      if (!(var_s1 & 0x1F))
      {
        func_002b5b68(0);
      }
    }
    var_s0 += 1;
  }
  while (var_s0 < 0x1DE8);
  return var_s1;
}
