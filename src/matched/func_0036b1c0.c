
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
void func_0036b1c0(int param_1, int param_2)
{
  undefined4 *puVar1;
  undefined4 *puVar2;
  puVar1 = (undefined4 *) param_2;
  if (param_2 != 0)
  {
    puVar2 = (undefined4 *) ((puVar1[1] * 4) + (*((int *) (param_1 + 0x4c))));
    *puVar1 = *puVar2;
    *puVar2 = (undefined4 *) param_2;
  }
  return;
}
