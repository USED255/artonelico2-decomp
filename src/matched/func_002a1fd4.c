
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
int baseelf_153();
int baseelf_87();
int func_0011299c();
int func_0013e2fc();
extern unsigned char D_0047A810[];
void func_002a1fd4(s32 arg0, void *arg1)
{
  u8 *new_var;
  func_0013e2fc(arg1);
  u8 temp = *((u8 *) arg1);
  if (temp != 0)
  {
    baseelf_87(arg0);
    func_0011299c(temp);
    s16 *d = (s16 *) (&D_0047A810);
    d[0x64] = 0;
    new_var = (u8 *) (((char *) arg1) + 0xA);
    d[0x4C] = 0;
    d[0x94] = -1;
    if (*new_var)
    {
      d[0x4C] = (d[0x64] = -1);
      d[0x94] = 0;
    }
    baseelf_153(arg0, d, *((s16 *) (((char *) arg1) + 6)), *((s16 *) (((char *) arg1) + 8)));
    return func_0011299c(0x80);
  }
}
