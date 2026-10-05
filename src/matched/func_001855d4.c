
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
extern int func_00185734();
extern int func_00185840();
extern int func_001858ac();
void func_001855d4(int param_1)
{
  ulong new_var;
  ulong *new_var2;
  new_var2 = (ulong *) (((int) param_1) + 0x460);
  func_001858ac();
  new_var = *new_var2;
  *new_var2 = 0xfffffffffffffffe & new_var;
  func_00185734(param_1);
  func_00185840(param_1);
  return;
}
