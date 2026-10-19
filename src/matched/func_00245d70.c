
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
extern int func_002468f0();
undefined4 func_00245d70(ulong *param_1)
{
  unsigned long new_var;
  long lVar1;
  undefined4 uVar2;
  new_var = 1;
  lVar1 = func_002468f0(0x1b2 + param_1, 0xffffffffffffffff);
  uVar2 = 1;
  if (lVar1 == new_var)
  {
    if (new_var)
    {
      if (param_1)
      {
        *((undefined2 *) param_1) = 2;
        uVar2 = 0xffffffff;
      }
      else
      {
        *((undefined2 *) param_1) = 2;
        uVar2 = 0xffffffff;
      }
    }
    *param_1 = (*param_1) | 0x100000000;
  }
  lVar1 = uVar2;
  return lVar1;
}
