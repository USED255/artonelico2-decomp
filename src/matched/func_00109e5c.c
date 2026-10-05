
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
void func_00109e5c(int param_1, undefined4 param_2)
{
  unsigned short new_var;
  *((undefined4 *) (param_1 + 8)) = param_2;
  *((undefined1 *) (param_1 + 0x40)) = 0;
  new_var = *((char *) (param_1 + 0x3d));
  if (new_var == '\0')
  {
    *((undefined1 *) (param_1 + 0x3d)) = 1;
  }
  return;
}
