
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
int func_001e5ed4();
int func_001e8e18();
extern unsigned char D_007AF2D0[];
void func_001e4538(void)
{
  int dummy;
  u32 *ptr = (u32 *) D_007AF2D0;
  void *base = (void *) ((*ptr) + 0x212E0);
  s16 stride;
  s32 i = 0;
  if ((*((s16 *) (((u8 *) base) + 0x3FC8C))) == (-1))
  {
    for (i = 0; i < 0x12; i++)
    {
      func_001e8e18((void *) (((u8 *) base) + (i * ((short) 0x38B0))));
    }

  }
  else
  {
    dummy = 0;
    for (;;)
    {
      void *v = func_001e5ed4(&dummy, *((s16 *) (((u8 *) base) + 0x3FC8C)));
      if (v == 0)
      {
        break;
      }
      func_001e8e18(v);
    }

  }
}
