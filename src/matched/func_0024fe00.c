
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
extern int func_0024fb10();
extern int func_0024fb58();
void func_0024fe00(int param_1)
{
  int iVar1;
  int iVar2;
  float fVar3;
  float fVar4;
  iVar1 = func_0024fb58();
  iVar2 = func_0024fb10();
  fVar4 = (float) iVar1;
  *((undefined4 *) (param_1 + 300)) = 0;
  fVar3 = iVar2;
  *((undefined4 *) (param_1 + 0x13c)) = 0;
  *((float *) (param_1 + 0x134)) = fVar4;
  iVar1 = param_1 + 0x138;
  *((float *) iVar1) = fVar4;
  *((float *) (param_1 + 0x130)) = fVar4;
  *((float *) (param_1 + 0x124)) = fVar3;
  *((float *) (param_1 + 0x128)) = fVar3;
  *((float *) (param_1 + 0x120)) = fVar3;
  return;
}
