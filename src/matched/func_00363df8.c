
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
extern int func_00360da0();
extern int LibcString_6();
extern int LibcString_16();
long func_00363df8(undefined8 param_1, undefined8 param_2)
{
  int iVar1;
  int lVar2;
  iVar1 = LibcString_16(param_2);
  lVar2 = func_00360da0(param_1, iVar1 + 1);
  if (lVar2 != 0)
  {
    LibcString_6(lVar2, param_2, iVar1 + 1);
  }
  return lVar2;
}
