
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
extern int func_0013f97c();
extern int func_0013fab4();
extern unsigned int D_007AF2D0;
void func_0013fb24(uint *param_1)
{
  int new_var;
  if (1 < (*param_1))
  {
    return;
  }
  new_var = D_007AF2D0 != 0;
  if (new_var)
  {
    func_0013fab4();
    return;
  }
  if (D_007AF2D0)
  {
    func_0013f97c();
    return;
  }
  else
  {
    func_0013f97c();
    return;
  }
}
