
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
undefined8 func_0028e1bc(int param_1)
{
  int new_var2;
  undefined4 *new_var3;
  int new_var;
  new_var3 = (undefined4 *) (param_1 + 4);
  *new_var3 = 0xffffffff;
  new_var = param_1 + 0x14;
  *((undefined4 *) (param_1 + 0xc)) = 0;
  if (1)
  {
 do { *((undefined4 *) (param_1 + 8)) = 0; *((undefined4 *) new_var) = 0; } while (0);
  }
  new_var2 = 0;
  *((undefined4 *) (param_1 + 0x18)) = new_var2;
  *((undefined4 *) (param_1 + 0x10)) = 0;
  return new_var2;
}
