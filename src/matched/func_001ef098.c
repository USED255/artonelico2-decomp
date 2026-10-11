
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
extern int func_001260a0();
extern int func_0012994c();
void func_001ef098(int param_1)
{
  undefined2 *new_var2;
  int new_var;
  int uVar1;
  new_var = 0xa8;
  if (((*((ulong *) (param_1 + new_var))) & 0x20000000000000) == 0)
  {
    func_001260a0(param_1 + 0x10);
    uVar1 = func_0012994c(param_1 + 0x10);
    new_var2 = (undefined2 *) (param_1 + 0xbc);
    *new_var2 = uVar1;
    *((undefined2 *) (param_1 + 0xd0)) = uVar1;
  }
  return;
}
