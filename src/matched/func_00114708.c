
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
extern int func_0011468c();
void func_00114708(undefined8 param_1, int param_2, int param_3, int param_4, int param_5)
{
  *((short *) (param_2 + 0xe)) = (*((short *) (param_2 + 0xe))) + param_3;
  func_0011468c(param_1, param_2, param_4 + ((*((short *) (param_2 + 0x10))) * 0x10), param_5 + ((*((short *) (param_2 + 0x12))) * 0x10));
  *((short *) (param_2 + 0xe)) = (*((short *) (param_2 + 0xe))) - param_3;
  return;
}
