
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
extern int func_00168630();
extern int func_001e0d9c();
extern unsigned int D_0079C90C;
void func_001ccb54(int param_1)
{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  if ((((*((char *) ((((*((short *) (param_1 + 0xea))) * 0x30) + D_0079C90C) + 0x1c))) & 0xFF) & 0xFF) == '\x01')
  {
    iVar3 = 0;
    iVar1 = *(*((int **) (param_1 + 0x110)));
    while (iVar1 != 0)
    {
      iVar1 = iVar3 * 0x50;
      iVar3 = iVar3 + 1;
      uVar2 = func_00168630((*((int *) (param_1 + 0x110))) + iVar1);
      func_001e0d9c(uVar2);
      iVar1 = *((int *) ((iVar3 * 0x50) + (*((int *) (param_1 + 0x110)))));
    }

  }
  return;
}
