
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
int func_00101770();
int func_001057e8();
int func_0010cd64();
extern unsigned char D_00A50548[];
void func_00107338(void)
{
  int t6;
  t6 = 8;
  if (((*((uint32_t *) D_00A50548)) & 0x100) && ((*((uint32_t *) (D_00A50548 + t6))) & 0x10))
  {
    func_0010cd64();
  }
  if ((*((uint32_t *) D_00A50548)) & 0x100)
  {
    if ((*((uint32_t *) (D_00A50548 + t6))) & 0x40)
    {
      func_001057e8();
      func_00101770();
    }
  }
  if (((*((uint32_t *) D_00A50548)) & 0x100) && ((*((uint32_t *) (D_00A50548 + t6))) & 0x10))
  {
  }
  if ((*((uint32_t *) (D_00A50548 + t6))) & 0x40)
  {
  }
  if (((*((uint32_t *) (D_00A50548 + t6))) & 0x10) == 0)
  {
    t6 = 0;
  }
  if ((*((uint32_t *) (D_00A50548 + t6))) & 0x40)
  {
  }
}
