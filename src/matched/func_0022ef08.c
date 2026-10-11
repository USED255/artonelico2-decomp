
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
extern int func_00205420();
extern int func_0022ea40();
extern int func_0022ead8();
void func_0022ef08(unsigned int param_1, undefined8 param_2, undefined8 param_3)
{
  undefined8 uVar1;
  uVar1 = func_0022ea40();
  func_00205420(uVar1);
  func_0022ead8(param_1, param_2, (*((short *) (((int) param_1) + 6))) + 1, param_3, 1);
  return;
}
