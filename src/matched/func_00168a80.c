
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
extern int baseelf_104();
void func_00168a80(int param_1)
{
  int iVar1;
  iVar1 = *((int *) (param_1 + 0x10000));
  if (iVar1 != 0)
  {
    baseelf_104(iVar1);
    *((int *) (param_1 + 0x10000)) = 0;
  }
  if ((*((int *) (param_1 + 0x10004))) != 0)
  {
    baseelf_104(*((int *) (param_1 + 0x10004)));
    *((undefined4 *) (param_1 + 0x10004)) = 0;
  }
  iVar1 = *((int *) (param_1 + 0x10018));
  if (iVar1 != 0)
  {
    baseelf_104(iVar1);
    *((undefined4 *) (param_1 + 0x10018)) = 0;
  }
  if ((*((int *) (param_1 + 0x1001c))) != 0)
  {
    baseelf_104(*((int *) (param_1 + 0x1001c)));
    *((undefined4 *) (param_1 + 0x1001c)) = 0;
  }
  *((undefined4 *) (param_1 + 0x10030)) = 0;
  return;
}
