
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
extern int func_00101b94();
extern int func_002d3900();
extern int func_002d46a0();
undefined4 func_00102210(undefined8 param_1)
{
  int lVar1;
  undefined4 uVar2;
  lVar1 = func_00101b94();
  uVar2 = 1;
  if (lVar1 == 0)
  {
    do
    {
      lVar1 = func_002d46a0(param_1);
    }
    while (lVar1 == 0);
    func_002d3900(1);
    uVar2 = 0;
  }
  return uVar2;
}
