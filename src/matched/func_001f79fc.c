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

extern int func_00104fa0();
extern int func_00105000();
extern int func_001e32a0();
extern int baseelf_81();
extern int func_001e3e88();
extern int baseelf_18();
extern int func_001e8a0c();
extern int func_001edc00();
extern int baseelf_12();
extern int func_00203900();
extern int func_002229e4();
extern unsigned int D_007AF2D0;

//==== 001f79fc func_001f79fc ====

void func_001f79fc(undefined8 param_1)

{
  undefined8 uVar1;
  undefined1 auStack_30 [16];
  
  uVar1 = baseelf_18(0x20);
  func_001e3e88();
  func_001e8a0c(auStack_30,uVar1);
  func_001e32a0(uVar1);
  func_001edc00(D_007AF2D0 + 0x10);
  func_00203900(D_007AF2D0 + 0x10);
  func_00104fa0(0x25800);
  func_00105000();
  func_002229e4(param_1);
  baseelf_12(uVar1,0x44,D_007AF2D0 + 0x10,10,0x4014000000000000,0x4049000000000000);
  baseelf_12(uVar1,0x16,0x14);
  baseelf_12(uVar1,0x36,0,10,0,0,0);
  baseelf_12(uVar1,0x37);
  baseelf_12(uVar1,0x2b,0xffffffffffffff01);
  baseelf_12(uVar1,0x16,0x28);
  baseelf_81();
  return;
}
