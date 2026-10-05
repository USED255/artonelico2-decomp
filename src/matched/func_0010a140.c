
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
extern int func_00108fd8();
extern int func_00109f24();
extern int func_0010a1a4();
void func_0010a140(undefined8 param_1, undefined8 param_2, undefined8 param_3, undefined8 param_4)
{
  undefined8 uVar1;
  long new_var;
  new_var = func_00108fd8(param_4, 1);
  uVar1 = new_var;
  uVar1 = func_0010a1a4(uVar1, 0x100, 1);
  func_00109f24(param_1, param_2, param_3, uVar1);
  return;
}
