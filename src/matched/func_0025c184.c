
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
extern int func_001357f4();
extern int func_00144390();
extern int func_0024a93c();
extern int func_00270e18();
extern int func_0027102c();
extern int func_00271080();
extern int func_00271120();
extern int func_0027c950();
void func_0025c184(int param_1)
{
  int iVar1;
  iVar1 = param_1 + 0x40c;
  func_0027102c(iVar1);
  func_00271080(iVar1, 9);
  func_00271120(iVar1, 0xb);
  *((undefined1 *) (param_1 + 0x40e)) = 0x10;
  *((undefined1 *) (param_1 + 0x40d)) = *((undefined1 *) (param_1 + 0x40f));
  func_00270e18(param_1 + 0x424);
  func_0027c950(param_1 + 0x438);
  func_0027c950(param_1 + 0x888);
  func_0011f004(param_1 + 0xd08);
  func_0011f090(param_1 + 0xd08, 0xe1e);
  func_0011f004(param_1 + 0xd38);
  func_0011f090(param_1 + 0xd38, 0xe1f);
  func_0024a93c(param_1 + 0xd70);
  func_0011f004(param_1 + 0x14e0);
  func_0011f090(param_1 + 0x14e0, 0xe2b);
  func_00144390(param_1 + 0x1510);
  *((undefined4 *) (param_1 + 0x1e5c)) = (*((undefined4 *) (param_1 + 0x1e00)) = 0xffffffff);
  func_001357f4(0xffffffffffffffff);
  return;
}
