
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
extern int func_001a2d78();
extern int func_001a3e9c();
extern unsigned int D_00BC4DC5;
void func_001a3ef4(undefined8 param_1, undefined8 param_2)
{
  char new_var;
  undefined1 uVar1;
  new_var = (uVar1 = D_00BC4DC5);
  func_001a2d78(1);
  func_001a3e9c(param_1, param_2);
  func_001a2d78(new_var);
  return;
}
