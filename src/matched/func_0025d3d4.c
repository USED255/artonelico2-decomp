
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
extern int func_0013f8dc();
extern int func_00144390();
extern int func_00270e18();
extern int func_0027102c();
extern int func_00271080();
extern int func_00271120();
extern int func_0027e684();
extern int func_0027e86c();
void func_0025d3d4(int param_1)
{
  int iVar2;
  undefined2 *puVar1;
  ;
  func_0027e684(param_1 + 0x40c);
  func_0027e86c(param_1 + 0x40c);
  func_0027102c(param_1 + 0x4bc);
  func_00271080(param_1 + 0x4bc, 9);
  func_00271120(param_1 + 0x4bc, 0x10);
  *((undefined1 *) (param_1 + 0x4be)) = 0x10;
  *((undefined1 *) (param_1 + 0x4bd)) = *((undefined1 *) (param_1 + 0x4bf));
  func_00270e18(param_1 + 0x4d4);
  func_00144390(param_1 + 0x4e8);
  func_0013f8dc();
  puVar1 = (undefined2 *) (param_1 + 0x16b8);
  *((undefined4 *) (param_1 + 0x16b4)) = 0xffffffff;
  iVar2 = 0x50;
  do
  {
    *puVar1 = 0;
    iVar2 = iVar2 + (-1);
    puVar1 = puVar1 + 1;
  }
  while ((-1) < iVar2);
  *((undefined4 *) (param_1 + 0x175c)) = 0;
  return;
}
