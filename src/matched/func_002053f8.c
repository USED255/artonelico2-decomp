
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
extern int func_00204fa8();
void func_002053f8(undefined8 param_1, long param_2)
{
  undefined4 uVar1;
  if (param_2 == 0)
  {
    if (uVar1 || param_2)
    {
      uVar1 = 8;
    }
    else
    {
      uVar1 = 8;
    }
  }
  else
  {
    uVar1 = 9;
  }
  func_00204fa8(param_1, uVar1);
  return;
}
