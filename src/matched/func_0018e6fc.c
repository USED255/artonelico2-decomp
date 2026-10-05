
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
extern int func_0018e57c();
extern int func_00190dc0();
extern int func_00190e68();
undefined8 func_0018e6fc(undefined8 param_1, long param_2)
{
  int uVar1;
  long lVar2;
  undefined8 uVar3;
  uVar3 = 0;
  uVar1 = func_0018e57c(param_1, 2);
  lVar2 = func_00190dc0(uVar1, 0);
  if (lVar2 == param_2)
  {
    uVar3 = func_00190e68(uVar1, 0);
  }
  return uVar3;
}
