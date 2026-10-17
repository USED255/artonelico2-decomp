
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
extern int baseelf_98();
unsigned int D_009DCA10 __attribute__((section(".sdata"), weak));
extern char D_009E53E0;
void func_00155be8(void)
{
  undefined4 uVar1;
  int iVar2;
  uVar1 = baseelf_98();
  iVar2 = D_009DCA10 * 4;
  D_009DCA10 = D_009DCA10 + 1;
  *((undefined4 *) (iVar2 + (&D_009E53E0))) = uVar1;
  return;
}
