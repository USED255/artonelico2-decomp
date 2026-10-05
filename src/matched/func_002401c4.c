
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
extern int func_0013ae70();
extern int func_0013aea0();
volatile unsigned int func_002401c4(int param_1, int param_2)
{
  func_0013ae70(param_1 + 0x498);
  *((int *) (param_1 + 0x4a0)) = param_2;
  if (1)
  {
    *((undefined4 *) (param_1 + 0x4a8)) = 1;
    *((int *) (param_1 + 0x4cc)) = param_2;
    *((int *) (param_1 + 0x498)) = param_2;
    *((int *) (param_1 + 0x4ac)) = param_2;
    *((undefined4 *) (param_1 + 0x49c)) = 0;
    *((undefined4 *) (param_1 + 0x4b0)) = 0;
    if (1)
    {
      *((undefined4 *) (param_1 + 0x4b8)) = 0;
      *((int *) (param_1 + 0x4b4)) = param_2 << 4;
      *((undefined4 *) (param_1 + 0x4a4)) = 0;
    }
    *((int *) (param_1 + 0x4bc)) = param_2 << 4;
    *((undefined4 *) (param_1 + 0x4c0)) = 0;
  }
  func_0013aea0(param_1 + 0x498);
  *((undefined1 *) (param_1 + 0x4c5)) = 0;
  return;
}
