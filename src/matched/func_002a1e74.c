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

extern int func_0024a8f0();

//==== 002a1e74 func_002a1e74 ====

int func_002a1e74(int param_1,undefined8 param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = func_0024a8f0(param_2,param_3 + -1);
  iVar3 = 0;
  iVar2 = 0;
  do {
    iVar4 = iVar1 * 0xf + iVar3;
    iVar3 = iVar3 + 1;
    if (*(short *)(iVar4 * 2 + param_1) != -1) {
      iVar2 = iVar2 + 1;
    }
  } while (iVar3 < 0xf);
  return iVar2;
}
