
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
extern int func_0018d9e0();
extern int func_00192a8c();
extern int func_00192e60();
extern int func_00192e68();
int func_0018db40(undefined8 param_1, undefined8 param_2)
{
  int iVar1;
  int lVar2;
  undefined8 uVar3;
  int iVar4;
  iVar4 = 0;
  iVar1 = func_0018d9e0();
  do
  {
    lVar2 = func_00192e60(iVar1);
    if (lVar2 != 0)
    {
      uVar3 = func_00192e68(param_1, iVar1);
      lVar2 = func_00192a8c(uVar3, param_2);
      if ((-1) < lVar2)
      {
        return iVar4;
      }
    }
    iVar4 = iVar4 + 1;
    iVar1 = iVar1 + 2;
  }
  while (iVar4 < 0x10);
  return -1;
}
