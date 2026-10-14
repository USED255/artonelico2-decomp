
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
extern int func_0029b418();
void func_0029b350(int param_1, undefined8 param_2)
{
  short sVar1;
  int iVar2;
  short *psVar3;
  iVar2 = 0;
  psVar3 = (short *) (param_1 + 10);
  while (1)
  {
    sVar1 = *psVar3;
    psVar3 = psVar3 + 4;
    if (sVar1 == (-1))
    {
      func_0029b418(param_1, iVar2, param_2);
      return;
    }
    iVar2 = iVar2 + 1;
    if (9 < iVar2)
    {
      break;
    }
    sVar1 = *psVar3;
  }

  return;
}
