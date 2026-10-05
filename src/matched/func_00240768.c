
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
extern int func_0011eddc();
extern int func_00144390();
extern int func_00145960();
extern int func_00271320();
extern int func_00271380();
extern int func_0027c950();
void func_00240768(int param_1)
{
  func_00145960();
  func_00271320(param_1 + 0x7ce4);
  func_00271380(param_1 + 0x7ce4, 0x14, 0x14);
  func_00144390(param_1 + 0x40c);
  func_0027c950(param_1 + 0xc78);
  func_0011eddc(param_1 + 0x10c8, 0x65);
  *((undefined1 *) (param_1 + 0x7d98)) = 0;
  *((undefined2 *) (param_1 + 0x7d96)) = 0xffff;
  *((undefined2 *) (param_1 + 0x7d9c)) = 0xffff;
  return;
}
