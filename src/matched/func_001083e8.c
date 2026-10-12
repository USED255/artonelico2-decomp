
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
extern unsigned char D_009E3900[];
void func_001083e8(void)
{
  int i = 0;
  do
  {
    int offset = i * 0x14;
    unsigned char *p = D_009E3900 + offset;
    if (1)
    {
      *((int32_t *) (p + 0x00)) = -1;
      *((int32_t *) (p + 0x04)) = 0;
      *((int32_t *) (p + 0x08)) = 0;
      i++;
    }
    *((int32_t *) (p + 0x0C)) = 0;
    *((int32_t *) (p + 0x10)) = -1;
  }
  while (i < 4);
}
