
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
int func_0029ae24();
void func_00299830(uint64_t param_1, int param_2)
{
  int var1;
  int var2;
  int ret = func_0029ae24(*((int32_t *) (param_2 + 0x410)), &var1, &var2);
  uint64_t new_var;
  new_var = (uint64_t) ret;
  if (ret != 0)
  {
    float f0 = (*((float *) (param_2 + 0x6DB0))) + ((float) var1);
    float f1 = (*((float *) (param_2 + 0x6DB4))) + ((float) var2);
    int a2 = (int) f0;
    int a3 = (int) f1;
    baseelf_153(param_1, new_var, a2, a3);
  }
}
