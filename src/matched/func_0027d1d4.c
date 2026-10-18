
typedef signed char s8;
typedef unsigned char u8;
typedef short s16;
typedef short u16;
typedef int s32;
typedef unsigned int u32;
typedef long long s64;
typedef unsigned long long u64;
typedef float f32;
typedef double f64;
typedef unsigned char undefined1;
typedef short undefined2;
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
typedef short uint16_t;
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
int func_0011f2bc();
int func_0013e2e8();
int func_0027d26c();
extern unsigned char D_0054AA00[];
void func_0027d1d4(unsigned int param_1)
{
  undefined1 *puVar1;
  int new_var2;
  int iVar2;
  unsigned char *new_var;
  undefined1 *puVar3;
  puVar1 = (undefined1 *) param_1;
  func_0011f2bc(puVar1 + 10);
  func_0013e2e8(puVar1);
  puVar1[4] = 0;
  puVar1[3] = 0x80;
  *puVar1 = 0;
  new_var2 = 1;
  new_var = D_0054AA00;
  puVar1[2] = 0;
  func_0027d26c(puVar1, *((uint16_t *) (new_var + 0x164)), *((uint16_t *) (new_var + 0x166)));
  puVar3 = puVar1 + 0x41c;
  iVar2 = 4;
  do
  {
    iVar2 = iVar2 + (-1);
    *puVar3 = 0xff;
    puVar3 = puVar3 + 1;
  }
  while ((-new_var2) < iVar2);
  puVar1[0x422] = 0;
  puVar1[0x421] = 0;
  *((short *) (puVar1 + 0x422)) = (*((short *) (puVar1 + 0x422))) & 0xfeff;
  return;
}
