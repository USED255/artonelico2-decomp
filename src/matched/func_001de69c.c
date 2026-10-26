
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
int func_001de69c(int param_1)
{
  int *new_var;
  int v0 = 0;
  int t4 = 0;
  int new_var2;
  do
  {
    int t7 = 0x30 * t4;
    t7 += param_1;
    int t6 = 0x101F0;
    new_var2 = 1;
    t4 += new_var2;
    new_var = &t7;
    t7 += t6;
    short val = *((short *) ((*new_var) + 0xC));
    t6 = 1;
    t7 = val ^ 0x4;
    v0 = ((*new_var) != 0) ? (1) : (v0);
  }
  while (t4 < 2);
  return (v0 == 0) ? (1) : (0);
}
