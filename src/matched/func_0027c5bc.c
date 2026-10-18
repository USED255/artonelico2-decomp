
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
extern int func_001918bc(short, int);
void func_0027c5bc(int param_1)
{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  iVar4 = 0;
  func_001918bc(*((undefined2 *) (param_1 + 0x28)), *((undefined1 *) (param_1 + 0x2a)));
  while (1)
  {
    iVar3 = *((int *) (param_1 + 0x24));
    iVar2 = iVar4 * 2;
    iVar4 = iVar4 + 1;
    sVar1 = *((short *) (iVar2 + iVar3));
    if ((sVar1 < 0) || ((func_001918bc(sVar1, -((uint) (*((byte *) (param_1 + 0x2a))))), 3 < iVar4)))
    {
      break;
    }
    iVar3 = *((int *) (param_1 + 0x24));
  }

  *((undefined1 *) (param_1 + 2)) = 0x10;
  *((undefined1 *) (param_1 + 1)) = *((undefined1 *) (param_1 + 4));
  return;
}
