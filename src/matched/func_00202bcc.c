
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
extern int baseelf_118();
void func_00202bcc(int param_1)
{
  short sVar1;
  if ((*((short *) (param_1 + 0x1720))) != 0)
  {
    baseelf_118(param_1 + ((*((short *) (param_1 + 0x1726))) * 0x50));
    sVar1 = (*((short *) (param_1 + 0x1726))) + 1;
    *((short *) (param_1 + 0x1726)) = (*((short *) (param_1 + 0x1726))) + 1;
    if (0x49 < sVar1)
    {
      *((undefined2 *) (param_1 + 0x1726)) = 0;
    }
    *((short *) (param_1 + 0x1720)) = (*((short *) (param_1 + 0x1720))) + (-1);
  }
  return;
}
