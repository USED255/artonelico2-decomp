
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
extern int func_001e2a98();
extern int baseelf_92();
extern int func_001f3e40();
void func_001f4d7c(void)
{
  undefined8 uVar1;
  long lVar2;
  uVar1 = baseelf_92();
  do
  {
    ;
    if (func_001e2a98(4) != 0)
    {
      return;
    }
    lVar2 = func_001f3e40(uVar1);
  }
  while (lVar2 == 1);
  return;
}
