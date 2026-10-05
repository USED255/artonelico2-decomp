
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
extern int func_0012b7c8();
extern int func_0012c2a0();
void func_0012c2dc(void)
{
  long lVar1;
  long new_var;
  int new_var2;
  lVar1 = func_0012c2a0();
  new_var2 = lVar1 != 0;
  new_var = lVar1;
  if (new_var2)
  {
    func_0012b7c8(new_var);
    return;
  }
 do { return; } while (0);
}
