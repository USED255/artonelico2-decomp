
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
extern int func_00143cc0();
void func_00143ca4(int param_1, undefined4 param_2, undefined4 param_3)
{
  int new_var;
  *((undefined4 *) (param_1 + 0x4fa8)) = param_3;
 new_var = 0; do { do { } while (0); } while (new_var);
  *((undefined4 *) (param_1 + 0x4fa4)) = param_2;
  func_00143cc0();
  return;
}
