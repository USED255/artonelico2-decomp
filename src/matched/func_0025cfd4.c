
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
extern int func_0011f004();
extern int func_0011f090();
extern int func_00144390();
extern int func_00270e18();
extern int func_0027102c();
extern int func_00271080();
extern int func_00271120();
extern int func_0027e684();
extern int func_0027e86c();
extern unsigned long long D_009DFCBC;
void func_0025cfd4(int param_1)
{
  int iVar1;
  iVar1 = param_1 + 0x4bc;
  func_0027e684(param_1 + 0x40c);
  func_0027e86c(param_1 + 0x40c);
  func_0027102c(iVar1);
  func_00271080(iVar1, 9);
  func_00271120(iVar1, 0xd);
  *((undefined1 *) (param_1 + 0x4be)) = 0x10;
  *((undefined1 *) (param_1 + 0x4bd)) = *((undefined1 *) (param_1 + 0x4bf));
  func_00270e18(param_1 + 0x4d4);
  func_00144390(param_1 + 0x4e8);
  func_0011f004(param_1 + 0xf64);
  *((undefined4 *) (param_1 + 0xfc0)) = 0;
  *((undefined4 *) (param_1 + 0xfc4)) = D_009DFCBC;
  func_0011f004(param_1 + 0xfc8);
  func_0011f090(param_1 + 0xfc8, 0xe2b);
  return;
}
