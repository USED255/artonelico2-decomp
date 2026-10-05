
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
extern int baseelf_4();
extern int func_0013f8dc();
extern int func_00144224();
extern int func_00145960();
extern int func_001505c4();
extern int func_001519f8();
extern int func_00151a54();
extern int func_0019f040();
extern unsigned int func_0019f5d8();
extern int func_001b04b0();
extern int func_001b8b24();
void func_0019c26c(void)
{
  int new_var2;
  unsigned int new_var;
  new_var2 = 3;
  func_00145960();
  func_0019f040();
  func_00151a54(0);
  func_001519f8();
  func_001505c4();
  func_0013f8dc();
  func_0019f5d8();
  baseelf_4();
  func_00144224();
  new_var = func_001b04b0(new_var2);
  new_var = new_var;
  if (new_var != 0)
  {
    func_001b8b24(new_var, 5);
    return;
  }
  return;
}
