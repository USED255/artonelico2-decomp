
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
undefined4 func_002376c4(undefined2 *param_1)
{
  int new_var;
  new_var = func_00140034();
  new_var = new_var;
  if (new_var == 2)
  {
    new_var = 10;
    *param_1 = new_var;
    *((uint *) (param_1 + 2)) = (*((uint *) (param_1 + 2))) | 1;
  }
  return 0xffffffff;
}
