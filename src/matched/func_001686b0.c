
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
void func_001686b0(undefined2 *param_1)
{
  int new_var;
  *param_1 = 0;
  param_1[8] = 0x32;
  param_1[2] = 1;
  new_var = 0 != 0;
  param_1[1] = 0;
 do { param_1[3] = 0x32; param_1[4] = 0x32; param_1[5] = 0x32; } while (new_var);
  param_1[6] = 0x32;
  param_1[7] = 0;
  return;
}
