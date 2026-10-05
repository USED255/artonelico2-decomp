
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
extern int func_00132500();
extern int func_00194430();
extern int func_0019470c();
extern int func_0019476c();
extern int func_001a1520();
void func_00239af8(undefined8 param_1, int param_2)
{
  int iVar1;
  iVar1 = (int) param_2;
  func_00132500(param_1, iVar1 + 0x894);
  func_001a1520(param_1);
  func_00132500(param_1, iVar1 + 0x864);
  func_00132500(param_1, iVar1 + 0x834);
  func_00132500(param_1, iVar1 + 0x894);
  func_00194430(param_1, param_2);
  func_0019470c(param_1, param_2);
  func_0019476c(param_1, param_2);
  return;
}
