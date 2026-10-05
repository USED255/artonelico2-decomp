
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
extern int baseelf_6();
extern int func_001531b8();
extern int func_00153830();
extern unsigned int D_0058CF1C;
undefined8 func_00153174(int param_1)
{
  undefined1 auStack_1f0[480];
  baseelf_6();
  D_0058CF1C = (undefined4) param_1;
  func_001531b8(auStack_1f0, param_1);
  func_00153830(auStack_1f0);
  return 0;
}
