
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
void func_0029dac8(int param_1)
{
  int iVar1;
  int iVar2;
  iVar2 = *((int *) (param_1 + 0x530));
  if ((iVar2 < (*((int *) (param_1 + 0x534)))) && ((iVar1 = (*((int *) (param_1 + 0x538))) + 1, *((int *) (param_1 + 0x538)) = iVar1, 0x1e < iVar1)))
  {
    *((undefined4 *) (param_1 + 0x538)) = 0;
    if (iVar2 < 5)
    {
      *((int *) (param_1 + 0x530)) = iVar2 + 1;
      return;
    }
    iVar2 = (*((int *) (param_1 + 0x540)) = (*((int *) (param_1 + 0x540))) + 1);
    if (0x13 < iVar2)
    {
      *((undefined4 *) (param_1 + 0x540)) = 0;
    }
    *((int *) (param_1 + 0x534)) = (*((int *) (param_1 + 0x534))) + (-1);
  }
  return;
}
