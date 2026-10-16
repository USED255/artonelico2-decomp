
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
extern int eepatch_4();
extern int eepatch_5();
unsigned int D_009DB7A8 __attribute__((section(".sdata"), weak));
extern volatile char D_009E2760;
void func_001063cc(void)
{
  eepatch_4();
  D_009DB7A8 = D_009DB7A8 + (-1);
  *((undefined4 *) ((&D_009E2760) + (D_009DB7A8 * 4))) = 0;
  eepatch_5();
  return;
}
