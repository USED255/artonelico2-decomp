
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
extern int baseelf_104();
extern int func_001023e0();
void func_00103b04(undefined8 param_1)
{
  int new_var2;
  long lVar1;
  long long pad;
  undefined1 auStack_20[16];
  int new_var;
  new_var = func_001023e0(param_1, auStack_20);
  lVar1 = new_var;
  new_var2 = lVar1 != 0;
  if (new_var2)
  {
    baseelf_104(lVar1);
  }
  return;
}
