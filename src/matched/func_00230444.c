/* Ghidra 伪 C 的最小 shim（实验用；不是最终类型恢复） */
typedef unsigned char      undefined;
typedef unsigned char      undefined1;
typedef unsigned short     undefined2;
typedef unsigned int       undefined4;
typedef unsigned long long undefined8;
typedef unsigned int       uint;
typedef unsigned long      ulong;
typedef unsigned short     ushort;
typedef unsigned char      uchar;
typedef long long          longlong;
typedef unsigned long long ulonglong;
typedef unsigned char      byte;
typedef unsigned char      code;
typedef unsigned char      bool;
typedef struct { int a[3]; } int3;
typedef struct { unsigned int a[3]; } uint3;
#define true 1
#define false 0
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
#define CONCAT44(a,b) (((unsigned long long)(a) << 32) | (unsigned int)(b))
#define CONCAT13(a,b) ((((unsigned int)(a)) << 24) | ((unsigned int)(b) & 0xffffff))
#define CONCAT22(a,b) ((((unsigned int)(a)) << 16) | ((unsigned int)(b) & 0xffff))
#define SUB41(a,b) ((unsigned int)(a))
#define SUB42(a,b) ((unsigned int)(a))
#define ZEXT14(a)  ((unsigned int)(unsigned char)(a))
#define ZEXT24(a)  ((unsigned int)(unsigned short)(a))
#define ZEXT48(a)  ((unsigned long long)(unsigned int)(a))
#define SEXT14(a)  ((int)(signed char)(a))
#define SEXT24(a)  ((int)(short)(a))
#define SEXT48(a)  ((long long)(int)(a))
#define LOWER(x)   ((unsigned int)(x))
#define HIDWORD(x) ((unsigned int)((unsigned long long)(x) >> 32))
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int  syscall(int);

extern int func_0010e498();
extern int func_0011299c();
extern int baseelf_87();
extern int func_0013f63c();
extern int func_00144d4c();
extern int func_002337e4();
extern int func_00234c5c();
extern int func_00270ed8();
extern int func_00271134();
extern int func_00276c30();
extern int func_00279418();
extern int func_0027a438();
extern int func_0027cd10();
extern int func_0027e71c();

//==== 00230444 func_00230444 ====

void func_00230444(undefined8 param_1,int param_2)

{
  baseelf_87();
  func_0010e498(param_1,1);
  func_0013f63c(param_1);
  func_0011299c(0x60);
  func_0027e71c(param_1,param_2 + 0x2984);
  func_0011299c(0x80);
  func_00144d4c(param_1,param_2 + 0x8ac);
  func_002337e4(param_2 + 0x28dc);
  func_00271134(param_1,param_2 + 0x2a34);
  func_0027cd10(param_1,param_2 + 0x45c);
  func_0027cd10(param_1,param_2 + 0x2e70);
  func_00279418(param_1,param_2 + 0x2a4c);
  func_0027a438(param_1,param_2 + 0x32c0);
  func_00270ed8(param_1,param_2 + 0x34f0);
  func_00234c5c(param_1,param_2 + 0x3504);
  func_00276c30(param_1,param_2 + 0x3534);
  return;
}
