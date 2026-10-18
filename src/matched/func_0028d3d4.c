
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
extern int func_001490c4();
extern volatile char D_00AF2470[];
void func_0028d3d4(void)
{
  int iVar1;
  iVar1 = 0;
  do
  {
    func_001490c4(7, iVar1);
    iVar1 = iVar1 + 1;
  }
  while (iVar1 < 0xf3);
  iVar1 = 0;
  do
  {
    (D_00AF2470[0xD8 + iVar1]) = 0;
    iVar1 = iVar1 + 1;
  }
  while (iVar1 < 0x20);
  return;
}
