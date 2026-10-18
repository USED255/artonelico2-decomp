/* Minimal shim for Ghidra pseudo C (experiment only; not a final type recovery) */
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



//==== 002dec30 func_002dec30 ====

void func_002dec30(int param_1,int *param_2,int *param_3,int *param_4,int *param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = *(int *)(param_1 + 8);
  iVar2 = *(int *)(param_1 + 0xc);
  iVar4 = iVar1 / 2;
  iVar3 = iVar4 + 0x1f;
  if (iVar3 < 0) {
    iVar3 = iVar4 + 0x3e;
  }
  *param_4 = (iVar3 >> 5) << 5;
  *param_5 = iVar2 / 2;
  *param_2 = iVar1;
  *param_3 = iVar2;
  return;
}
