
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
extern int baseelf_7();
extern int baseelf_73();
extern int baseelf_4();
extern int func_0018cec0();
extern int func_0019f584();
extern int func_001a04f0();
extern int func_00253514();
extern int func_00253728();
extern int func_0025741c();
extern unsigned int D_00BB8524;
void func_0018d11c(void)
{
  short new_var;
  baseelf_4();
  baseelf_73((int) 0, 1);
  do
  {
    baseelf_7();
    new_var = D_00BB8524;
    switch (new_var)
    {
      case 1:
        func_0018cec0(2);
        break;

      case 2:
        func_001a04f0();
        break;

      case 3:
        func_00253514();
        break;

      case 4:
        func_00253728();
        break;

      case 5:
        func_0025741c();
        break;

      case 6:
        func_0019f584();

    }

  }
  while (1);
}
