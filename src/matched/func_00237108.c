
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
extern int func_00140034();
undefined4 func_00237108(undefined2 *param_1)
{
  uint *new_var2;
  int new_var;
  undefined2 *new_var3;
  long lVar1;
  new_var = func_00140034();
  lVar1 = new_var;
  if (lVar1 == 2)
  {
    new_var = 1;
    *param_1 = 1;
    new_var3 = param_1;
    new_var2 = (uint *) (new_var3 + 2);
    *((uint *) (new_var3 + 2)) = (*new_var2) | new_var;
  }
  new_var = 0xffffffff;
  return new_var;
}
