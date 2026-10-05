
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
undefined4 func_00241dd0(undefined2 *param_1)
{
  undefined2 *new_var3;
  long lVar1;
  int new_var2;
  uint *new_var4;
  undefined2 *new_var;
  new_var2 = (unsigned int) func_00140034();
  lVar1 = new_var2;
  if (lVar1 == 2)
  {
    new_var2 = 0xf;
    *param_1 = new_var2;
    new_var3 = param_1 + 2;
    new_var = new_var3;
    new_var4 = &(*((uint *) new_var));
    *((uint *) new_var) = (*new_var4) | 1;
  }
  return 0xffffffff;
}
