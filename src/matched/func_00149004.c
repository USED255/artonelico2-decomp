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

extern int func_00149104();

//==== 00149004 func_00149004 ====

typedef struct { int pad[2]; int v; char rest[44]; } T56B; extern T56B D_007F5B20[];
extern char D_00BB9298[];

void func_00149004(void)

{
  int iVar1;
  
  iVar1 = 0;
  do {
    if ((D_007F5B20[iVar1].v != -1) &&
       (D_00BB9298[D_007F5B20[iVar1].v * 4] != '\0')) {
      func_00149104(8,iVar1,1);
    }
    iVar1 = iVar1 + 1;
  } while (iVar1 < 0x2c);
  return;
}
