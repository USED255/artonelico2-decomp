
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
extern int func_001eade4();
extern int func_001eaf64();
extern int func_0020696c();
extern int func_00208368();
void func_00208cd8(undefined8 param_1, undefined8 param_2, undefined8 param_3)
{
  int lVar1;
  lVar1 = func_001eade4(param_1, 0x1a);
  if (((lVar1 != 0) && ((lVar1 = func_00208368(param_1, param_2, 0x1a, param_3), lVar1 == (-1)))) && ((lVar1 = func_001eaf64(param_1, 0x1a), 0 < lVar1)))
  {
    func_0020696c(param_1, param_2, lVar1, 0, 0);
  }
  return;
}
