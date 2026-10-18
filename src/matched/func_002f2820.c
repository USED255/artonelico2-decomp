
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
extern int func_003127f8();
void func_002f2820(int param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)
{
  undefined4 uVar1;
  *((undefined4 *) (param_1 + 0xd74)) = param_3;
  uVar1 = *(*((undefined4 **) (param_1 + 0x2030)));
  *((undefined4 *) (param_1 + 0xd78)) = param_4;
  *((undefined4 *) (param_1 + 0xd7c)) = param_2;
  func_003127f8(uVar1);
  return;
}
