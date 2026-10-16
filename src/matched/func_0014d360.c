
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
extern int func_0014dc08();
unsigned int D_009DC5D0 __attribute__((section(".sdata"), weak)) = 0xFFFFFFFF;
unsigned int D_009DC5E0 __attribute__((section(".sdata"), weak));
void func_0014d360(void)
{
  int iVar1;
  int new_var;
  new_var = D_009DC5D0;
  if ((-1) < new_var)
  {
    D_009DC5E0 = 0;
    D_009DC5D0 = -1;
    iVar1 = 2;
    do
    {
      func_0014dc08(iVar1, 0xffffffffffffffff);
      new_var = 1;
      iVar1 = iVar1 + new_var;
    }
    while (iVar1 < 0x12);
  }
  return;
}
