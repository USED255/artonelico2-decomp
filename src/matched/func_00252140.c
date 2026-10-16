
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
extern int func_00155cc8();
extern int func_00157940();
extern int func_0015a0ac();
void func_00252140(int param_1)
{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  func_00155cc8(0x1a9000);
  func_00157940(0x80000);
  iVar1 = *((int *) (param_1 + 0x40c));
  iVar3 = 0x16;
  if ((iVar1 != 10) && ((iVar3 = 0x17, iVar1 != 0xb)))
  {
    iVar3 = iVar1 + 6;
  }
  ;
  *((undefined4 *) (param_1 + 0x8170)) = func_0015a0ac(param_1 + 0x470, 0x32, iVar3, param_1 + 0x420);
  return;
}
