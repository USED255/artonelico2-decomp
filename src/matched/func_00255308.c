
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
extern int func_0013f8dc();
extern int func_00140034();
undefined4 func_00255308(ulong *param_1)
{
  long lVar1;
  lVar1 = func_00140034();
  if (lVar1 == 2)
  {
    func_0013f8dc();
 do { if (param_1) { *((undefined2 *) param_1) = 4; } else { *((undefined2 *) param_1) = 4; } } while (0);
    *param_1 = (lVar1 = (*param_1) | 0x100000000);
  }
  return 0xffffffff;
}
