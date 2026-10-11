
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
extern int func_00115638();
extern int func_00116350();
void func_001156e8(undefined8 param_1, int param_2, int param_3, int param_4, undefined8 param_5, undefined8 param_6)
{
  int iVar1;
  for (; param_3 <= param_4; param_3 = param_3 + iVar1)
  {
    func_00116350(param_1, ((int) param_2) + (param_3 * 0x30), param_5, param_6);
    iVar1 = func_00115638(param_2);
  }

  return;
}
