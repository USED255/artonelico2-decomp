
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
extern int func_002a0c1c();
extern unsigned int D_00A50550;
undefined4 func_001a021c(ulong *param_1)
{
  if ((D_00A50550 & 0x2000) != 0)
  {
 do { if (param_1) { func_002a0c1c(); *((undefined2 *) param_1) = 2; } else { func_002a0c1c(); *((undefined2 *) param_1) = 2; } } while (0);
    *param_1 = (*param_1) | 0x100000000;
  }
  return 0xffffffff;
}
