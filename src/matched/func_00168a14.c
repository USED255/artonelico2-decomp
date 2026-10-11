
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
void func_00168a14(int param_1)
{
  int iVar1;
  int iVar2;
  iVar1 = 0x1ff;
  if (0 < (*((int *) (param_1 + 0x10008))))
  {
    iVar1 = 0;
    do
    {
      iVar2 = iVar1 * 4;
      iVar1 = iVar1 + 1;
      *((undefined4 *) (iVar2 + (*((int *) (param_1 + 0x10000))))) = 0;
    }
    while (iVar1 < (*((int *) (param_1 + 0x10008))));
  }
  iVar1 = 0x1ff;
  do
  {
    *((undefined2 *) (param_1 + 4)) = 0;
    iVar1 = iVar1 + (-1);
    *((undefined2 *) (param_1 + 10)) = 0;
    param_1 = param_1 + 0x80;
  }
  while ((-1) < iVar1);
  return;
}
