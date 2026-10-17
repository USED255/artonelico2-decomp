
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
void func_00291354(int param_1)
{
  undefined2 *new_var;
  *((undefined1 *) (param_1 + 0x74)) = 0;
  *((undefined2 *) (param_1 + 0x4a)) = 0x3200;
  *((undefined1 *) (param_1 + 0x44)) = 0x80;
  *((undefined1 *) (param_1 + 0x45)) = 0x80;
  *((undefined2 *) (param_1 + 0x68)) = 100;
  new_var = (undefined2 *) (param_1 + 0x48);
  *new_var = 0;
  *((undefined4 *) (param_1 + 0x5c)) = 1;
  *((undefined2 *) (param_1 + 0x6c)) = 0;
  *((undefined2 *) (param_1 + 0x6e)) = 0;
  *((undefined4 *) (param_1 + 0x70)) = 0;
  *((undefined4 *) (param_1 + 0x50)) = 0;
  *((undefined4 *) (param_1 + 0x54)) = 0;
  *((undefined4 *) (param_1 + 0x58)) = 0;
  *((undefined4 *) (param_1 + 100)) = (short) 0;
  *((undefined1 *) (param_1 + 0x46)) = 0x80;
  return;
}
