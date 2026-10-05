
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
uint func_0036b0e8(undefined8 param_1, uint *param_2, int param_3, long param_4)
{
  uint uVar1;
  uint auStack_10[4];
  uVar1 = 0;
  if (param_2 == ((uint *) 0x0))
  {
    param_2 = auStack_10;
  }
  if ((param_3 != 0) && ((uVar1 = 0xffffffff, param_4 != 0)))
  {
    *param_2 = (uint) (*((byte *) param_3));
    uVar1 = (uint) ((*((byte *) param_3)) != 0);
  }
  return uVar1;
}
