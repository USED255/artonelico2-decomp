
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
extern int func_001b0704();
extern int func_001b1014();
extern int func_001b5f08();
extern int func_001d895c();
void func_001d89d4(undefined8 param_1)
{
  int iVar1;
  undefined8 new_var;
  new_var = 0;
  iVar1 = new_var;
  func_001b0704();
  do
  {
    new_var = param_1;
    func_001d895c(new_var, iVar1);
    iVar1 = 1 + iVar1;
  }
  while (iVar1 < 0x13b);
  func_001b1014();
  func_001b5f08();
  return;
}
