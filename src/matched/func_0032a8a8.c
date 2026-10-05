
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
extern int func_00322d98();
extern int func_00327660();
extern int func_00328e08();
extern int func_0032a128();
extern int func_0032a528();
void func_0032a8a8(undefined8 param_1)
{
  long lVar1;
  long lVar2;
  if (lVar1 || lVar2)
  {
    func_0032a528();
    lVar1 = func_0032a128(param_1);
  }
  else
  {
    func_0032a528();
    lVar1 = func_0032a128(param_1);
  }
  if (lVar1 != 0)
  {
    do
    {
      lVar2 = func_00322d98(lVar1);
      if (lVar2 == 2)
      {
        return;
      }
      func_00328e08();
      lVar2 = func_00327660(param_1);
    }
    while (lVar2 != 5);
  }
  return;
}
