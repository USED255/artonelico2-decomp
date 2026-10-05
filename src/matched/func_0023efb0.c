
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
extern int func_00180d6c();
extern unsigned int D_009DFCD4;
void func_0023efb0(int param_1)
{
  unsigned int new_var;
  new_var = D_009DFCD4;
  if ((new_var != 0) && ((new_var = *((short *) (((long long) param_1) + 0x1348))) != (-1)))
  {
    func_00180d6c(*((short *) (param_1 + 0x1348)));
    *((undefined2 *) (param_1 + 0x1348)) = 0xffff;
  }
  return;
}
