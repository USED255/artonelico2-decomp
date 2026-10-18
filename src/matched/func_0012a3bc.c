
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
extern int func_0012988c();
extern int func_0012994c();
float func_0012a3bc(unsigned int param_1)
{
  short sVar2;
  int iVar3;
  int new_var3;
  short uVar1;
  int iVar4;
  int new_var;
  int iVar5;
  float new_var2;
  uVar1 = *((short *) (((int) param_1) + 0x70));
  iVar3 = func_0012994c();
  new_var = ((int) param_1) + 0x72;
  sVar2 = *((short *) new_var);
  iVar4 = func_0012988c(param_1, uVar1, sVar2);
  new_var3 = func_0012988c(param_1, uVar1, sVar2 + 1);
  ;
  new_var2 = (float) (iVar3 - iVar4);
  return new_var2 / ((float) (new_var3 - iVar4));
}
