
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
extern M2C_UNK D_0060B180;
extern M2C_UNK D_00BB84C8;
void func_0017cafc(void)
{
  s32 temp_t6;
  s32 var_t4;
  void **temp_t5;
  var_t4 = 0;
  do
  {
    temp_t6 = var_t4 * 0x780;
    temp_t5 = (void **) ((char *) (&D_00BB84C8) + var_t4 * 4);
    var_t4 = var_t4 + 1;
    *temp_t5 = &D_0060B180;
    *temp_t5 = temp_t6 + (*temp_t5);
  }
  while (var_t4 < 0x14);
}
