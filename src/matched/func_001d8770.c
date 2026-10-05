
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
extern volatile unsigned long long func_001d7b04();
extern int func_001d86d8();
void func_001d8770(undefined8 param_1, undefined8 param_2, undefined8 param_3)
{
  undefined8 new_var;
  long lVar1;
  lVar1 = func_001d7b04();
  if (lVar1 != 0)
  {
    func_001d86d8(lVar1, param_3);
    return;
  }
  new_var = param_3;
  if (new_var || lVar1)
  {
    return;
  }
  else
  {
    return;
  }
}
