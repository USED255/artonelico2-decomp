
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
extern int func_001df9d8();
extern int func_001dfa1c();
void func_001df9a4(void)
{
  int new_var;
  long lVar1;
  int new_var2;
  lVar1 = -1;
  new_var2 = lVar1;
  new_var = new_var2;
  lVar1 = func_001dfa1c();
  new_var2 = lVar1;
  if (1)
  {
    if (new_var2 != new_var)
    {
      func_001df9d8(lVar1);
      return;
    }
  }
  return;
}
