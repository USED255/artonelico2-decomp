
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
int func_001b5a70();
int func_001d7b04();
int func_001d8318();
extern unsigned char D_007A0A00[];
void func_001d7eec(int unused, int arg1)
{
  uint32_t s1;
  int32_t v0;
  long long new_var;
  int32_t s0;
  int32_t s2;
  new_var = 0x30;
  s2 = arg1;
  s1 = *((uint32_t *) ((((unsigned char *) D_007A0A00) + (((intptr_t) arg1) * 0x34)) + new_var));
  v0 = func_001d7b04();
  if ((v0 != 0) && (s1 != 0))
  {
    func_001d8318((int32_t) s1, v0);
    func_001b5a70(v0 + 4, arg1);
  }
}
