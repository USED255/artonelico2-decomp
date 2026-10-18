
typedef unsigned char undefined;
typedef unsigned char char;
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
extern int func_00125af0();
extern int func_00125c1c(int, short, short);
extern int func_0012988c();
void func_00273484(int *param_1)
{
  short uVar1;
  char auStack_a0[144];
  if ((*param_1) != 0)
  {
    func_00125af0(auStack_a0);
    func_00125c1c(auStack_a0, *((short *) ((*param_1) + 0x16)), *((short *) ((*param_1) + 0x18)));
    uVar1 = (*((short *) (((int) param_1) + 6)) = func_0012988c(auStack_a0, *((short *) ((*param_1) + 0x18)), *((char *) ((*param_1) + 0x1b))));
  }
  return;
}
