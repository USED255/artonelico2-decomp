
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short undefined2;
typedef unsigned int undefined4;
typedef unsigned long long undefined8;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned short ushort;
typedef unsigned char uchar;
typedef long long longlong;
typedef unsigned long long ulonglong;
typedef unsigned char byte;
typedef unsigned char code;
typedef unsigned char bool;
typedef struct 
{
  int a[3];
} int3;
typedef struct 
{
  unsigned int a[3];
} uint3;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int baseelf_98();
extern int func_001677ec();
void func_0016791c(int *param_1, int param_2, undefined8 param_3)
{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int new_var;
  param_1[3] = 0;
  param_1[1] = 10000;
  *param_1 = param_2;
  iVar3 = 0;
  iVar1 = baseelf_98(0x10, (param_2 * 0x50) + 0x50);
  new_var = 2;
  param_1[2] = iVar1;
  if (0 < param_2)
  {
    do
    {
      iVar1 = iVar3 * 0x50;
      iVar3 = iVar3 + 1;
      func_001677ec(param_1[new_var] + iVar1, param_3);
      *((undefined4 *) (iVar1 + param_1[2])) = 0;
    }
    while (iVar3 < param_2);
  }
  puVar2 = (undefined4 *) ((iVar3 * 0x50) + param_1[2]);
  puVar2[0x10] = (*puVar2 = 0);
  return;
}
