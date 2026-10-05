
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
extern int baseelf_73();
extern int func_0018cec0();
extern int func_0018d004();
extern int func_0018d11c();
extern int func_0026f0c4();
extern int func_00270bfc();
void func_0018d1fc(void)
{
  unsigned int lVar1;
  baseelf_73(0, 1);
  func_0018d004(1);
  func_0026f0c4();
  lVar1 = func_00270bfc();
  if (lVar1 == 0)
  {
    func_0018d004(1);
  }
  func_0018cec0(1);
  func_0018d11c();
  return;
}
