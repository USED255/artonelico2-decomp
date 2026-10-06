
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
int LibcStdlib_34();
int func_001e7d34();
int func_001eade4();
int func_001eaf8c();
int func_00233d40();
extern unsigned char D_007AF2D0[];
void func_0020867c(void *arg0, u8 *arg1)
{
  s32 var_s1;
  s16 t6;
  var_s1 = func_00233d40(arg0, 0xD, 0);
  if (func_001eade4(arg0, 0x23) != 0)
  {
    if (func_001e7d34(arg0) != 0)
    {
      if (var_s1 > 0)
      {
        var_s1 += func_001eaf8c(arg0, 0x23);
      }
    }
  }
  t6 = *((s16 *) (((uintptr_t) arg0) + 0x1E));
  if (t6 == 1)
  {
    u32 base = *((u32 *) (&D_007AF2D0[0]));
    u32 *ptr;
    u32 val = *((u32 *) (base + 0xC1CA4));
    if (val & 2)
    {
      var_s1 = 0x64;
    }
  }
  s32 rem = (LibcStdlib_34() >> 8) % 100;
  if (rem < var_s1)
  {
    *arg1 |= 0x80;
  }
}
