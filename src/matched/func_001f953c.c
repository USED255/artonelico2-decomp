
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
extern int baseelf_12();
void func_001f953c(int param_1, undefined8 param_2)
{
  short sVar1;
  sVar1 = *((short *) ((*((int *) (((int) param_1) + 0xb24))) + 0x3a));
  if (sVar1 < 1)
  {
    sVar1 = 1;
  }
  baseelf_12(param_1, 0x18, 0, param_2, param_1, param_1);
  if (sVar1 == 1)
  {
    baseelf_12(param_1, 10, 3, 0, 10);
    baseelf_12(param_1, 0x16, 0x1e);
    sVar1 = 3;
    baseelf_12(param_1, 0x15, 0, param_2, param_1, param_1);
    baseelf_12(param_1, 10, sVar1, 0x80, 0x14);
  }
  else
  {
    baseelf_12(param_1, 0x21, 6);
    baseelf_12(param_1, 0, 7, 1);
    baseelf_12(param_1, 0x22);
    baseelf_12(param_1, 0x15, 0, param_2, param_1, param_1);
    baseelf_12(param_1, 0x21, 7);
    baseelf_12(param_1, 0x22);
  }
  return;
}
