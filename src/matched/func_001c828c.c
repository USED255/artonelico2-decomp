
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
extern unsigned int D_0079C90C;
bool func_001c828c(int param_1)
{
  bool bVar1;
  short *psVar2;
  int iVar3;
  iVar3 = 1;
  bVar1 = 0;
  if ((((*((ulong *) (param_1 + 0xf0))) >> 0x39) & iVar3) != 0)
  {
    psVar2 = (short *) (((*((short *) (param_1 + 0xea))) * 0x30) + D_0079C90C);
    iVar3 = (int) (*((char *) (((int) psVar2) + 0x29)));
    if ((*psVar2) == 2)
    {
      iVar3 = 5;
    }
    if ((iVar3 - 5U) < 2)
    {
      bVar1 = (*((char *) (((int) psVar2) + 0x2d))) == '\x01';
    }
  }
  return bVar1;
}
