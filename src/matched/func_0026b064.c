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



//==== 0026b064 func_0026b064 ====

void func_0026b064(undefined8 param_1,undefined1 *param_2)

{
  *(undefined1 *)(*(int *)(param_2 + 4) + 0x1c) = *param_2;
  *(undefined1 *)(*(int *)(param_2 + 4) + 0x1d) = param_2[1];
  *(undefined1 *)(*(int *)(param_2 + 4) + 0x1e) = param_2[2];
  if ((*(uint *)(param_2 + 8) & 0x100) == 0) {
    *(undefined1 *)(*(int *)(param_2 + 4) + 0x1c) = 0x50;
    *(undefined1 *)(*(int *)(param_2 + 4) + 0x1d) = 0x50;
    *(undefined1 *)(*(int *)(param_2 + 4) + 0x1e) = 0x50;
    *(undefined1 *)(*(int *)(param_2 + 4) + 0x1f) = 0x50;
  }
  else {
    *(undefined1 *)(*(int *)(param_2 + 4) + 0x1f) = param_2[3];
  }
  if ((*(uint *)(param_2 + 8) & 0x200) == 0) {
    *(undefined1 *)(*(int *)(param_2 + 4) + 0x1f) = 0;
  }
  return;
}
