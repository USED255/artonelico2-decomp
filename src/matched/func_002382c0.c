
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
extern int func_0011299c();
extern int func_001129d8();
extern int baseelf_87();
extern int func_0013787c();
extern int func_00238838();
extern int func_0024fc2c();
extern int func_00270ed8();
void func_002382c0(undefined8 param_1, short *param_2)
{
  short sVar1;
  undefined8 uVar2;
  int new_var;
  uVar2 = func_001129d8();
  func_0013787c(param_1);
  baseelf_87(param_1);
  sVar1 = *param_2;
  new_var = 0;
  if (((sVar1 != new_var) && ((-1) < sVar1)) && (sVar1 <= (7 - 1)))
  {
    func_0024fc2c(param_1, param_2 + 0x220);
    func_00238838(param_1, param_2 + 0x210);
    func_00270ed8(param_1, param_2 + 0x206);
  }
  func_0011299c(uVar2);
  return;
}
