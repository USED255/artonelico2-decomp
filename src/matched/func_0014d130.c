
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
extern unsigned char D_00AF2818[];
void func_0014d130(void)
{
  int new_var;
  s32 var_t4;
  void *temp_t6;
  var_t4 = 0;
  do
  {
    temp_t6 = ((uintptr_t) D_00AF2818) + (var_t4 * 4);
    new_var = -1;
    var_t4 += 1;
    *((s16 *) ((u8 *) temp_t6)) = new_var;
    *((s16 *) (((u8 *) temp_t6) + 2)) = new_var;
  }
  while (var_t4 < 0x64);
}
