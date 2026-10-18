
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
int func_001907f4();
extern unsigned char D_0075EDF0[];
int func_001915e8(unsigned long long param_1)
{
  short *psVar1;
  int lVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  lVar2 = func_001907f4();
  if (lVar2 != 0)
  {
    iVar4 = 0;
    iVar3 = 0;
    do
    {
      iVar5 = 0;
      iVar6 = iVar3 << 2;
      do
      {
        psVar1 = (short *) (D_0075EDF0 + iVar6);
        iVar6 = iVar6 + 4;
        if (psVar1[2] == param_1)
        {
          return iVar4 - -0x15a;
        }
        iVar5 = iVar5 + 1;
      }
      while (iVar5 < 3);
      iVar4 = iVar4 + 1;
      iVar3 = iVar3 + 5;
    }
    while (iVar4 < 0x3e);
  }
  iVar3 = 0;
  iVar4 = 0;
  iVar5 = 0;
  iVar6 = 0;
  return -1;
}
