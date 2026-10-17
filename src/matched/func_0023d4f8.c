
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
extern int func_0010de2c();
extern int baseelf_87();
extern int func_0023e21c();
unsigned int D_009DF2A0 __attribute__((section(".sdata"), weak));
void func_0023d4f8(int param_1)
{
  int iVar1;
  int iVar2;
  iVar1 = D_009DF2A0;
  if (D_009DF2A0 != 0)
  {
    baseelf_87();
    iVar2 = (int) param_1;
    *((undefined4 *) (iVar2 + 0x54)) = 1;
    *((undefined4 *) (iVar2 + 0x58)) = 1;
    *((undefined4 *) (iVar2 + 0x5c)) = 1;
    *((undefined4 *) (iVar2 + 0x50)) = 1;
    func_0010de2c(param_1, 0, 1);
    func_0023e21c(param_1, iVar1);
    return;
  }
  return;
}
