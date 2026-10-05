
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
extern int func_0013f8dc();
extern int func_0013f900();
extern int func_00140dcc();
extern int func_00140dd8();
void func_00193e08(void)
{
  long lVar1;
  undefined8 uVar2;
  int new_var;
  uVar2 = func_0013f900();
  lVar1 = uVar2;
  new_var = lVar1 != 0;
  if (new_var)
  {
    uVar2 = func_00140dd8();
    func_0013f8dc();
    func_00140dcc(uVar2);
    return;
  }
  return;
}
