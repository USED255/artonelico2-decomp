
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
extern int func_0012ddd8();
extern int func_00132e70();
extern int func_00132eec();
void func_0012f1e0(undefined8 param_1, int param_2, int param_3)
{
  ;
  if ((*((int *) (((param_3 * 0xf0) + param_2) + 0xd0))) == 0)
  {
    func_00132e70();
    func_00132eec(param_1);
  }
  func_0012ddd8(param_1, (param_3 * 0xf0) + param_2);
  return;
}
