
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
int baseelf_4();
int baseelf_7();
int func_001e29a0();
int func_001e2b88();
int func_001ed884();
extern unsigned char D_007AF2D0[];
int baseelf_45(void)
{
  s32 **orig_s0 = *((s32 ***) (&D_007AF2D0));
  s32 s1 = *(*orig_s0);
  baseelf_4();
  while (1)
  {
    baseelf_7();
    if (func_001e2b88(orig_s0) == 0)
    {
      break;
    }
    s32 **s0 = orig_s0;
    if (func_001ed884((s32 **) (((char *) s0) + 0x10)) == 0)
    {
      break;
      return 0;
    }
    func_001e29a0(s1, s0);
  }

}
