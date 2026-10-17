
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
unsigned int D_009DC5CC __attribute__((section(".sdata"), weak));
extern char D_009E42C0;
void func_0014d164(void)
{
  int iVar1;
  int iVar2;
  D_009DC5CC = 0;
  iVar1 = 0;
  do
  {
    iVar2 = iVar1 * 8;
    iVar1 = iVar1 + 1;
    *((undefined2 *) ((&D_009E42C0) + iVar2)) = 0xffff;
  }
  while (iVar1 < 0x100);
  return;
}
