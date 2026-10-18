
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
extern char D_00AD8000;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int baseelf_6();
extern int func_0012b940();
extern int func_001357f4();
extern int func_00180588();
extern int func_0023ed28();
unsigned int D_009DF2A0 __attribute__((section(".sdata"), weak));
extern unsigned int D_009DFCD4;
void func_0023b010(unsigned int param_1)
{
  func_001357f4(0xffffffffffffffff);
  if ((D_009DFCD4 != 0) && ((*((char *) (((int) param_1) + 0x192a))) == '\x01'))
  {
    func_00180588();
  }
  func_0023ed28(param_1);
  D_009DF2A0 = 0;
  baseelf_6();
  func_0012b940((&D_00AD8000));
  return;
}
