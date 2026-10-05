
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
extern int func_00124a6c();
void func_001248cc(int param_1)
{
  int new_var;
  func_00124a6c();
  *((undefined4 *) (param_1 + 0x18)) = 0;
  *((uint *) (param_1 + 0x30)) = (*((uint *) (param_1 + 0x30))) | 1;
  *((undefined4 *) (param_1 + 0x24)) = 0;
  *((undefined4 *) (param_1 + 0x28)) = 0;
  new_var = 0;
  *((undefined4 *) (param_1 + 0x2c)) = new_var;
  *((undefined4 *) (param_1 + 0x20)) = 0x2d0;
  return;
}
