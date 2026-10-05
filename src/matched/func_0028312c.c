
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
extern int func_0027607c();
extern int func_00282dac();
extern int func_00282de8();
void func_0028312c(unsigned int param_1)
{
  int iVar1;
  func_00282de8();
  iVar1 = (int) param_1;
  *((undefined1 *) (iVar1 + 0x434)) = *((undefined1 *) (iVar1 + 0x438));
  *((undefined1 *) (iVar1 + 0x16ec)) = *((undefined1 *) (iVar1 + 0x16f0));
  *((undefined1 *) (iVar1 + 0x436)) = 0;
  *((undefined1 *) (iVar1 + 0x16ee)) = 0;
  func_0027607c(iVar1 + 0x1da4, 1);
  *((undefined1 *) (iVar1 + 0x1da4)) = *((undefined1 *) (iVar1 + 0x1da8));
  *((undefined1 *) (iVar1 + 0x1da5)) = *((undefined1 *) (iVar1 + 0x1da7));
  *((undefined1 *) (iVar1 + 0x1da6)) = 0x10;
  func_00282dac(param_1);
  *((undefined2 *) (iVar1 + 0x33e4)) = 0xffff;
  return;
}
