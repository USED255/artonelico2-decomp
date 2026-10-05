
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
extern int baseelf_98();
extern int baseelf_104();
extern int func_00169c88();
extern int func_0016a040();
extern int func_0016a064();
void func_0016a124(undefined8 param_1, unsigned int param_2)
{
  undefined4 uVar1;
  int iVar2;
  uVar1 = baseelf_98(0x10, 0x8000);
  iVar2 = (int) param_2;
  *((undefined4 *) (iVar2 + 0x10030)) = uVar1;
  func_0016a040(param_2);
  func_00169c88(*((undefined4 *) (iVar2 + 0x10030)), param_2, 0);
  func_0016a064(param_1, param_2);
  baseelf_104(*((undefined4 *) (iVar2 + 0x10030)));
  return;
}
