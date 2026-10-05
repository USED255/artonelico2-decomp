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

extern int func_001e32a0();
extern int baseelf_81();
extern int baseelf_56();
extern int baseelf_14();
extern int baseelf_45();
extern int baseelf_48();
extern int baseelf_111();
extern int baseelf_200();
extern int baseelf_12();
extern int baseelf_116();
extern unsigned int D_007AF2D0;

//==== 0022e4b0 func_0022e4b0 ====

void func_0022e4b0(int param_1)

{
  undefined8 uVar1;
  int iVar2;
  
  if (*(short *)(param_1 + 2) == 0x15) {
    uVar1 = baseelf_14();
    if (*(short *)((int)uVar1 + 0xae4) == 0) {
      baseelf_200(D_007AF2D0 + 0xbe3b0,0);
      baseelf_81();
      iVar2 = *(int *)(param_1 + 0x54);
      if (iVar2 == 0) {
        iVar2 = *(int *)(param_1 + 0x58);
      }
      baseelf_56(iVar2);
      baseelf_111(D_007AF2D0 + 0xbe380);
      baseelf_48(D_007AF2D0 + 0x980,D_007AF2D0 + 0x10,0x10,0);
      baseelf_45();
      baseelf_116(uVar1,uVar1,2,2);
      baseelf_12(uVar1,0,1,0);
      func_001e32a0(uVar1);
      baseelf_200(D_007AF2D0 + 0xbe3b0,0xffffffffffffffff);
    }
  }
  return;
}
