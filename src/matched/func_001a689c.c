
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
extern int func_001a67d0();
extern int func_001a682c();
extern unsigned long func_001a6864();
extern int func_001a69e8();
void func_001a689c(void)
{
  long lVar1;
  undefined8 uVar2;
  int iVar3;
  iVar3 = 0;
  do
  {
    lVar1 = func_001a6864(iVar3);
    if (lVar1 != 0)
    {
      uVar2 = func_001a682c(iVar3);
      func_001a69e8(iVar3, uVar2);
      func_001a67d0(iVar3, 0);
    }
    iVar3 = iVar3 + 1;
  }
  while (iVar3 < 0x65);
  return;
}
