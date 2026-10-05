
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
extern int func_001519a8();
extern int func_00151b00();
ulong func_001519f8(void)
{
  ulong uVar1;
  int iVar2;
  int uVar3;
  iVar2 = 0;
  uVar3 = 0;
  do
  {
    uVar1 = func_001519a8(iVar2);
    iVar2 = iVar2 + 1;
    uVar3 = uVar3 | uVar1;
  }
  while (iVar2 < 100);
  func_00151b00();
  return uVar3;
}
