
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
int func_0019bf58();
int func_0019c1bc();
extern unsigned char D_009DFCE4[];
int func_0019ca68(void *ptr, s32 val)
{
  s32 tmp8 = *((s32 *) (((uint8_t *) ptr) + 8));
  func_0019bf58(ptr, tmp8);
  s32 *g = (s32 *) D_009DFCE4;
  s32 gv = *g;
  gv = gv + 1;
  *g = gv;
  *((s32 *) (((uint8_t *) ptr) + 0x4188)) = val;
  *((s32 *) (((uint8_t *) ptr) + 0x4184)) = -1;
  func_0019c1bc(ptr);
  gv = *g;
  if (gv >= (0 + 1))
  {
    ;
    *g = gv - 1;
  }
  return *((s32 *) (((uint8_t *) ptr) + 0x4184));
}
