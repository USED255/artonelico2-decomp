
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
extern int func_001dfa1c();
extern volatile char D_00BFD384;
void func_001dfb10(undefined8 param_1, undefined4 *param_2)
{
  unsigned int lVar1;
  undefined4 *new_var;
 do { lVar1 = func_001dfa1c(); new_var = param_2; } while (0);
  if (lVar1 != (-1))
  {
    *new_var = (&D_00BFD384) + (((int) lVar1) * 0x34);
  }
  return;
}
