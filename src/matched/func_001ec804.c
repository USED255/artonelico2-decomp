
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short short;
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
extern int func_00125c1c();
extern int func_001e3e88();
extern int baseelf_173();
void func_001ec804(int param_1, int param_2, undefined8 param_3)
{
  if (param_2 == (-1))
  {
    *((ulong *) (param_1 + 0xad8)) = (*((ulong *) (param_1 + 0xad8))) & 0xffefffffffffffff;
    *((short *) (param_1 + 0xae0)) = 0xffff;
    baseelf_173(param_1 + 0xa30, 0, 0);
  }
  else
    if (((*((ulong *) (param_1 + 0xad8))) & 0x10000000000000) == 0)
  {
    *((short *) (param_1 + 0xae0)) = (short) param_2;
    func_001e3e88();
    func_00125c1c(param_1 + 0xa40, *((short *) (param_1 + 0xae0)), param_3);
    *((ulong *) (param_1 + 0xad8)) = (*((ulong *) (param_1 + 0xad8))) | 0x10000000000000;
  }
  return;
}
