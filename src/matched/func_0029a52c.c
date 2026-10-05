
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
extern int func_0029a2b4();
undefined4 func_0029a52c(unsigned long long param_1)
{
  short *psVar1;
  int iVar2;
  iVar2 = 0;
  do
  {
    psVar1 = (short *) func_0029a2b4(iVar2);
    iVar2 = iVar2 + 1;
    if ((*psVar1) == param_1)
    {
      return *((undefined4 *) (psVar1 + 2));
    }
  }
  while (iVar2 < 8);
  return 0;
}
