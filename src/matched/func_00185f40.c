
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
extern unsigned int D_0061D4C0;
int func_00185f40(unsigned int param_1)
{
  int iVar1;
  int iVar2;
  int iVar3;
  iVar1 = 0;
  iVar2 = 0;
  do
  {
    iVar3 = (iVar2 * 0x470) + D_0061D4C0;
    iVar2 = iVar2 + 1;
    if ((((*((byte *) (iVar3 + 0x460))) & 1) != 0) && ((*((char *) (iVar3 + 0x1a))) == '\0'))
    {
      if ((*((short *) (iVar3 + 0x8e))) == param_1)
      {
        iVar1 = iVar1 + 1;
      }
    }
  }
  while (iVar2 < 100);
  return iVar1;
}
