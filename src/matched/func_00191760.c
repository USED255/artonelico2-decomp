
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short short;
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
extern int func_00190378();
extern int func_00190408();
extern unsigned int D_0075EDF4;
volatile short func_00191760(undefined8 param_1, int param_2)
{
  int iVar1;
  short *puVar2;
  long lVar3;
  int iVar4;
  lVar3 = func_00190378();
  if (lVar3 == 7)
  {
    iVar1 = func_00190408(param_1);
    iVar4 = 0;
    puVar2 = (short *) (((unsigned char *) (&D_0075EDF4)) + (iVar1 * 0x14));
    do
    {
      if (puVar2[1] == param_2)
      {
        return *puVar2;
      }
      iVar4 = iVar4 + 1;
      puVar2 = puVar2 + 2;
    }
    while (iVar4 < 3);
  }
  return 0xffff;
}
