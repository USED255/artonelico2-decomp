
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
extern int func_002a0294();
undefined4 func_00221a18(void)
{
  undefined4 uVar1;
  int new_var;
  unsigned int new_var2;
  long lVar2;
  lVar2 = func_002a0294();
  uVar1 = 0xffffffff;
  new_var = 1;
  if (lVar2 == (-new_var))
  {
    uVar1 = 0;
 new_var2 = 0; do { } while (new_var2);
  }
  return uVar1;
}
