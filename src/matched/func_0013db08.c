
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
extern long func_0013d6e8();
extern unsigned int D_00585544;
uint func_0013db08(undefined8 param_1)
{
  long lVar1;
  uint uVar2;
  undefined1 auStack_50[64];
  lVar1 = func_0013d6e8(param_1, 0xffffffffffffffff, auStack_50);
  uVar2 = 0;
  if (((D_00585544 & 0xffff) != 2) && ((uVar2 = 1, lVar1 < 1)))
  {
    uVar2 = D_00585544;
  }
  return uVar2;
}
