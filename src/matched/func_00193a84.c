
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
int func_0018d83c();
int func_0018d908();
int func_0018d958();
int func_0018dee8();
int func_00192c20();
extern unsigned char D_00757970[];
void func_00193a84(unsigned long long param_1)
{
  int lVar4;
  int iVar2;
  int iVar3;
  int *new_var;
  BOOL bVar1 = 0;
  while ((lVar4 = func_0018d958(param_1)) < 99)
  {
    iVar2 = func_0018d958(param_1);
    new_var = &(*((int *) (D_00757970 + (iVar2 * 4))));
    iVar3 = func_0018d83c(param_1);
    if (iVar3 < (*new_var))
    {
      break;
    }
    bVar1 = 1;
    func_0018d908(param_1, 1);
  }

  if (bVar1)
  {
    func_0018dee8(param_1);
    func_00192c20(param_1);
  }
}
