
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
extern unsigned int D_0079C90C;
undefined4 func_001cba28(int param_1)
{
  short new_var2;
  short new_var;
  new_var2 = *((undefined2 *) (((new_var = *((short *) (param_1 + 0xea))) * 0x30) + D_0079C90C));
  switch (new_var2)
  {
    case 0:

    case 4:

    case 0x1b:

    case 0x20:

    case 0x21:

    case 0x28:

    case 0x2c:
      return 0;

    default:
      return 1;

  }

}
