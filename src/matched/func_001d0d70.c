
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
extern volatile unsigned long func_001a1d9c();
extern int func_001a3d4c();
extern int func_001a3d88();
extern int func_001a7190();
extern int func_001b613c();
extern int func_001b726c();
void func_001d0d70(int param_1)
{
  undefined8 uVar1;
  uVar1 = func_001a1d9c();
  func_001a3d4c();
  func_001a3d88(uVar1, 1);
  func_001a7190(uVar1, param_1 + 0x70);
  func_001b613c(0x3c, 0xffffffffffffff01, 0);
  func_001b613c(0x3c, 0, 0xf);
  func_001b613c(0x3e);
  func_001b613c(0x12, 3);
  func_001b613c(0xb, 3, 0);
  func_001b613c(0x12, 3);
  func_001b726c();
  return;
}
