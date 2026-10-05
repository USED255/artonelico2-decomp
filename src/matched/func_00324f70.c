
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
undefined4 func_00324f70(int param_1, int param_2)
{
  int new_var;
  *((int *) (param_1 + 0x5c)) = param_2;
  new_var = *((int *) (param_1 + 0x18));
  if (new_var < param_2)
  {
    *((int *) (param_1 + 0x5c)) = new_var;
  }
  return new_var = *((undefined4 *) (param_1 + 0x5c));
}
