
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
extern int func_001a3f60();
extern unsigned int D_0079C908;
extern unsigned int D_00BC0950;
void func_001a4124(undefined8 param_1, undefined8 param_2, undefined8 param_3)
{
  int iVar1;
  short new_var;
  iVar1 = D_0079C908 + ((new_var = D_00BC0950) * 0x78);
  func_001a3f60(param_1, iVar1, iVar1 + 0xc, iVar1 + 0x12, param_2, param_3);
  return;
}
