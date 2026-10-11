
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
extern int baseelf_87();
extern int func_0011f118();
extern int func_001326f4();
extern int func_0013787c();
extern int func_0013fec0();
extern int func_00144d4c();
extern int func_00146880();
extern int func_00270ed8();
extern int func_00271134();
extern int func_00278ff4();
extern int func_00279418();
extern int func_0027c844();
extern int func_0027e71c();
void func_0025f274(undefined8 param_1, short *param_2)
{
  baseelf_87();
  if ((*param_2) == 1)
  {
    param_1++;
    param_1--;
    func_0013787c();
    func_0027c844(param_1, param_2 + 0x93e);
    func_0011f118(param_1, param_2 + 0x976);
    func_0011f118(param_1, param_2 + 0x95e);
    func_00146880(param_1);
    func_0013fec0(param_1);
    return;
  }
  func_0027e71c(param_1, param_2 + 0x206);
  func_00271134(param_1, param_2 + 0x25e);
  func_00270ed8(param_1, param_2 + 0x26a);
  func_00279418(param_1, param_2 + 0x274);
  func_00144d4c(param_1, param_2 + 0x486);
  func_00278ff4(param_1, param_2 + 0x8bc);
  func_001326f4(param_1, param_2 + 0x98e);
  return;
}
