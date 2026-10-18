
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
extern int func_002fc888();
void func_002fcc10(int param_1, undefined4 *param_2)
{
  int aiStack_30[4];
  *param_2 = 0;
  if (((param_1 != 0) && ((func_002fc888(param_1, aiStack_30), aiStack_30[0] != 0))) && (((*((int *) (((int) param_1) + 0xdc0))) != 0) || (0 < (*((int *) (((int) param_1) + 0xda8))))))
  {
    *param_2 = 1;
  }
  return;
}
