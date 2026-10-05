
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
extern int func_00192a64();
extern int func_001934e8();
undefined4 func_0019320c(undefined8 param_1)
{
  undefined8 uVar1;
  long lVar2;
  int iVar3;
  iVar3 = 0;
  do
  {
    uVar1 = func_00192a64(param_1, iVar3);
    iVar3 = iVar3 + 1;
    ;
    if (func_001934e8(uVar1) != 0)
    {
      return 1;
    }
  }
  while (iVar3 < 2);
  return 0;
}
