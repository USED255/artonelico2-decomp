
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
extern int func_00140bb8();
extern int func_0027ca20();
extern int func_0027cc88();
extern unsigned int D_009DFAF8;
extern unsigned int D_009DFB00;
void func_0028bd9c(unsigned int param_1)
{
  *((undefined **) (param_1 + 0x22e0)) = &D_009DFAF8;
  *((undefined2 *) (param_1 + 0x22e4)) = (*((undefined2 *) (param_1 + 0x22dc)) = 4);
  *((undefined2 *) (param_1 + 0x22e6)) = (*((undefined2 *) (param_1 + 0x22de)) = 3);
  *((undefined **) (param_1 + 0x22e8)) = &D_009DFB00;
  func_0027ca20(param_1 + 0x1a5c, 0, 2, 1, param_1 + 0x22dc);
  func_0027cc88(param_1 + 0x1a5c, 0x14, 300);
  *((undefined1 *) (param_1 + 0x1a8a)) = 0x10;
  *((undefined1 *) (param_1 + 0x1a89)) = *((undefined1 *) (param_1 + 0x1a8b));
  func_00140bb8(param_1 + 0x22ec, 0);
  return;
}
