
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
extern int func_00100508();
extern int func_00100510();
extern int func_00100518();
unsigned int D_009DE038 __attribute__((section(".sdata"), weak));
unsigned int D_009DE03C __attribute__((section(".sdata"), weak));
unsigned int D_009DE040 __attribute__((section(".sdata"), weak));
unsigned int D_009DE068 __attribute__((section(".sdata"), weak));
void func_001dd9a8(void)
{
  int new_var;
  new_var = D_009DE068;
  if (0 < new_var)
  {
    D_009DE038 = func_00100508();
    D_009DE03C = func_00100510();
    D_009DE040 = func_00100518();
  }
  return;
}
