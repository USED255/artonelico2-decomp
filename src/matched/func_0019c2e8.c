
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
M2C_UNK func_00145960();
extern volatile unsigned char D_00585990;
void func_0019c2e8(s32 arg0)
{
  s32 var_t5;
  s8 *var_s0;
  void *temp_t6;
  func_00145960();
  var_s0 = arg0 + 0x9F9;
  var_t5 = 0;
  do
  {
    *var_s0 = 0;
    var_s0 += 1;
    temp_t6 = (var_t5 * 0x120) + (&D_00585990);
    var_t5 += 1;
    *((s8 *) (((s8 *) temp_t6) + 6)) = 0;
  }
  while (var_t5 < 5);
}
