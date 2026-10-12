
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
int func_00325120();
int func_00326430();
int func_00326448();
int func_00324de8(void *arg0)
{
  s8 new_var2;
  uint8_t *new_var;
  new_var = ((uint8_t *) arg0) + 0x4D;
  func_00325120();
  func_00326430();
  new_var2 = *((s8 *) new_var);
  s8 v = new_var2;
  if (v == 1)
  {
    *((s8 *) (((uint8_t *) arg0) + (new_var2 = 0x4A))) = v;
  }
  *((s8 *) (((uint8_t *) arg0) + 0x49)) = 0;
  return func_00326448();
}
