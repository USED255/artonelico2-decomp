
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
s32 func_00304960(void *arg0, void *arg1)
{
  register s32 a0 asm("a0");
  unsigned int new_var;
  register s32 a1 asm("a1");
  register s32 a2 asm("a2");
  register s32 v0 asm("v0");
  register s32 v1 asm("v1");
  if (a1)
  {
    a0 = *((s32 *) (((uint8_t *) arg0) + 4));
    a2 = 0x51;
  }
  else
  {
    a0 = *((s32 *) (((uint8_t *) arg0) + 4));
    a2 = 0x51;
  }
  if (a0 == a2)
  {
    v0 = 4;
    goto L0;
  }
  v0 = 4;
  v1 = 0x61;
  if (a0 == v1)
  {
    v0 = 5;
    goto L0;
  }
  v0 = 5;
  v1 = *((s32 *) (((uint8_t *) a1) + 0x94));
  a0 = 5;
  new_var = a2;
  v0 = 4;
  v1 = v1 ^ new_var;
  v0 = (v1) ? (a0) : (v0);
  L0:
  return v0;

}
