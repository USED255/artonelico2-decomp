
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short short;
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
extern char D_0097B7F8;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int func_001409d0();
extern int func_001a1d9c();
extern int func_0023585c(short, int);
extern int func_0023590c();
extern int func_00235ec8();
extern int LibcStdio_47();
void func_00237d7c(int param_1)
{
  undefined8 uVar1;
  undefined1 auStack_110[256];
  ;
  LibcStdio_47(auStack_110, 0x100, (&D_0097B7F8), func_00235ec8(*((short *) (param_1 + 0x162c))));
  func_001409d0(auStack_110, 9, 0xffffffffffffffff, 0x23, 0xffffffffffffffff, 0xffffffffffffffff, 1);
  func_0023585c(*((short *) (param_1 + 0x162c)), 1);
  uVar1 = func_001a1d9c();
  func_0023590c(*((short *) (param_1 + 0x162c)), uVar1);
  return;
}
