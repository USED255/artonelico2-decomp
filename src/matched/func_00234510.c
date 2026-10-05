
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
extern int func_00233e14();
extern int func_00233fc8();
void func_00234510(undefined8 param_1, unsigned int param_2, int param_3)
{
  int iVar1;
  int iVar2;
  int new_var;
  int new_var2;
  new_var2 = 0;
  iVar1 = func_00233e14(2);
  if ((new_var = 0) < iVar1)
  {
    param_3 = -param_3;
    iVar2 = new_var2;
    if (new_var2 < iVar1)
    {
      do
      {
        param_3 = param_3 / 2;
        if (param_3 < 10)
        {
          param_3 = 10;
        }
        func_00233fc8(param_1, param_2, param_3);
        iVar2 = iVar2 + 1;
      }
      while (iVar2 < iVar1);
    }
  }
  return;
}
