
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
extern char D_00BC3400;
extern char D_00BC0950;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int func_001a643c();
extern int func_001b0998();
extern int func_001b0a60();
extern int func_001b4384();
extern int func_001cdecc();
undefined4 func_001a1fd4(unsigned int param_1, undefined8 param_2, undefined8 param_3, undefined8 param_4, undefined8 param_5)
{
  int lVar1;
  if (((param_1 & 1) != 0) && ((lVar1 = func_001a643c((&D_00BC0950)), lVar1 != 0)))
  {
    return 1;
  }
  if (((param_1 & 2) != 0) && ((lVar1 = func_001b0998(param_2, param_3, param_4, param_5), lVar1 != 0)))
  {
    if (param_1)
    {
      return 1;
    }
    else
    {
      return 1;
    }
  }
  if (((param_1 & 4) != 0) && ((lVar1 = func_001b4384(param_2, param_3, param_4, param_5), lVar1 != 0)))
  {
    return 1;
  }
  if (((param_1 & 8) != 0) && ((lVar1 = func_001cdecc((&D_00BC3400), param_2, param_3, param_4, param_5), lVar1 != 0)))
  {
    return 1;
  }
  if (((param_1 & 0x20) != 0) && ((lVar1 = func_001b0a60(param_2, param_3, param_4, param_5), lVar1 != 0)))
  {
    return 1;
  }
  return 0;
}
