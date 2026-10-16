
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
extern volatile unsigned int func_001d75e8();
void func_001b7c10(int param_1)
{
  ulong uVar1;
  uVar1 = func_001d75e8(param_1 + 0x70);
  *((ulong *) (param_1 + 0x270)) = (*((ulong *) (param_1 + 0x270))) & 0xfffffe1fffffffff;
  *((ulong *) (param_1 + 0x270)) = (*((ulong *) (param_1 + 0x270))) | ((uVar1 & 0xf) << 0x25);
  return;
}
