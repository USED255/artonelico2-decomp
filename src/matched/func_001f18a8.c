
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
int baseelf_87();
int func_0010dfc0();
int func_002917d0();
int func_00292128();
int func_0029216c();
extern unsigned char D_00A504E0[];
extern unsigned char D_00AD7F78[];
void func_001f18a8(s32 *arg0, void *arg1)
{
  unsigned char (*new_var)[];
  s32 temp_s6;
  s32 var_a2;
  s32 var_s1;
  new_var = &D_00A504E0;
  baseelf_87(&D_00A504E0);
  temp_s6 = *((s32 *) D_00AD7F78);
  func_0010dfc0(*arg0, 0, 3);
  func_00292128((void *) (((uintptr_t) arg1) + 0xF6C0), (void *) (((uintptr_t) arg1) + 0xF700));
  var_s1 = 0;
  if ((*((s16 *) (((uintptr_t) arg1) + 0xF6B0))) > 0)
  {
    var_a2 = 0 << 7;
    do
    {
      var_a2 = var_s1 << 7;
      func_002917d0(new_var, arg1, (void *) ((((uintptr_t) arg1) + var_a2) + 0xEAB0), (void *) (((uintptr_t) arg1) + 0xCC));
      var_s1 += 1;
    }
    while (var_s1 < (*((s16 *) (((uintptr_t) arg1) + 0xF6B0))));
  }
  func_0029216c((void *) (((uintptr_t) arg1) + 0xF700));
  func_0010dfc0(*arg0, 0, temp_s6);
}
