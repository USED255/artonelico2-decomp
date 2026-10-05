
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
extern int func_001b3904();
extern int func_001b3ce0();
extern int func_001b3dd0();
extern int func_001b5cd4();
extern int func_001d7b04();
void func_001a62f4(undefined8 param_1, undefined8 param_2)
{
  long lVar1;
  int new_var;
  lVar1 = func_001d7b04(param_2, param_1);
  new_var = lVar1 != 0;
  if (new_var)
  {
    func_001b3904();
    func_001b5cd4(lVar1);
    func_001b3ce0();
    func_001b3dd0();
    return;
  }
  return;
}
