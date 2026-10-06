
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
extern volatile unsigned long long func_0029cd04();
int func_0029cd3c(long param_1)
{
  long lVar1;
  int iVar2;
  int iVar3;
  iVar2 = 0;
  iVar3 = 0;
  do
  {
    lVar1 = func_0029cd04(iVar2);
    iVar2 = iVar2 + 1;
    if (lVar1 == param_1)
    {
      iVar3 = iVar3 + 1;
    }
  }
  while (iVar2 < 0x3c);
  return iVar3;
}
