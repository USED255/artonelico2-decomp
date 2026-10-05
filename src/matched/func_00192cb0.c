
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
extern int func_00192c20();
void func_00192cb0(undefined8 param_1)
{
  int iVar1;
  undefined1 *puVar2;
  long new_var;
  new_var = func_0018d9e0();
  iVar1 = new_var;
  puVar2 = (undefined1 *) (iVar1 + 1);
  iVar1 = 0xf;
  do
  {
    *puVar2 = 0;
    iVar1 = iVar1 + (-1);
    puVar2 = puVar2 + 2;
  }
  while ((-1) < iVar1);
  func_00192c20(param_1);
  return;
}
