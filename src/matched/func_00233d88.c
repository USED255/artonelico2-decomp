
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
int func_001e5dd0();
int func_001e9c88();
int func_0029e26c();
int func_00233d88(int a0, int a1)
{
  if (((unsigned int) a0) >= 0x3E)
  {
    return 0;
  }
  int sum = 0;
  int flag = 0;
  for (;;)
  {
    int ret1 = func_001e5dd0(&flag);
    if (ret1 == 0)
    {
      break;
    }
    void *ptr = (void *) ((intptr_t) ret1);
    int ret2 = func_001e9c88(ptr, 0x20);
    if (ret2 == 0)
    {
    }
    else
    {
      int16_t val = *((int16_t *) (((uint8_t *) ptr) + 0x1E));
      int ret3 = func_0029e26c(val, a0, a1);
      sum += ret3;
    }
  }

  return sum;
}
