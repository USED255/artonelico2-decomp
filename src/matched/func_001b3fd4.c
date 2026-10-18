
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
extern int func_001c5f78();
extern unsigned int D_00BC6790[];
void func_001b3fd4(void)
{
  int iVar1;
  int iVar2;
  if (iVar2)
  {
    iVar1 = 0;
  }
  else
  {
    iVar1 = 0;
  }
  do
  {
    if ((D_00BC6790[0x81E + iVar1]) != 0)
    {
      func_001c5f78((D_00BC6790[0x81E + iVar1]));
    }
    iVar1 = iVar1 + 1;
    iVar2 = iVar1;
    iVar1 = iVar2;
  }
  while (iVar2 < 0x80);
  return;
}
