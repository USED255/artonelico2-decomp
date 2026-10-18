
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
typedef unsigned char uint8_t;
typedef signed char int8_t;
typedef unsigned short uint16_t;
typedef short int16_t;
typedef unsigned int uint32_t;
typedef int int32_t;
typedef unsigned long long uint64_t;
typedef long long int64_t;
typedef unsigned int uintptr_t;
typedef int intptr_t;
typedef unsigned int size_t;
typedef int ssize_t;
typedef int ptrdiff_t;
typedef int BOOL;
int func_00103b04();
int func_0012bac8();
extern unsigned char D_00561710[];
extern unsigned char D_00A50600[];
extern unsigned char D_00AD8000[];
void func_0012a6e0(s32 arg0)
{
  s16 temp_t6;
  s16 var_s1;
  s32 s2;
  s32 s3;
  func_0012bac8(&D_00AD8000, arg0);
  var_s1 = 0;
  do
  {
    temp_t6 = *((s16 *) ((((u8 *) D_00561710) + (arg0 * 0xF8)) + (var_s1 * 2)));
    if (((u32) (temp_t6 - 0x16D9)) < 0x709U)
    {
      { s32 *p8 = (s32 *) (((u8 *) D_00A50600) + (temp_t6 * 0x48)); func_00103b04(p8[2]); }
    }
    var_s1 += 1;
  }
  while (var_s1 < 0x1A);
}
