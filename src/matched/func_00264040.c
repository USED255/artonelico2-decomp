
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
int func_00264040(int param_1)
{
  int iVar1;
  int iVar2;
  iVar1 = 0;
  ;
  while (1)
  {
    if ((*((int *) (param_1 + 4))) == 0)
    {
      return param_1;
    }
    iVar1 = iVar1 + 1;
    if (4 < iVar1)
    {
      break;
    }
    iVar2 = *((int *) (param_1 + 0x24));
    param_1 = param_1 + 0x20;
  }

  return 0;
}
