
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
extern int func_001919e4();
undefined4 func_00292d4c(void)
{
  long lVar1;
  int iVar2;
  int new_var;
  iVar2 = 0;
  do
  {
    lVar1 = func_001919e4(iVar2 + 0x122);
    iVar2 = iVar2 + 1;
    new_var = lVar1 != 0;
    if (new_var)
    {
      return 0;
    }
  }
  while (iVar2 < 0x38);
  return 1;
}
