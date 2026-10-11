
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
extern int baseelf_6();
extern int func_0014fb58();
extern int func_001e1398();
extern int func_001e4030();
extern int func_001f79fc();
extern int func_001f7b14();
extern int func_001f800c();
extern int func_00223758();
extern int func_002346b8();
extern unsigned int D_007AF2D0;
void func_001f794c(void)
{
  long lVar1;
  undefined8 uVar2;
  undefined1 auStack_170[320];
  undefined1 auStack_30[32];
  func_002346b8(D_007AF2D0 + 0xc1ca8);
  func_001f79fc(auStack_170);
  func_001f7b14(auStack_170, auStack_30);
  ;
  if ((func_001e1398() != 0) && (((*((uint *) (D_007AF2D0 + 0xc1ca4))) & 2) != 0))
  {
    uVar2 = func_001e4030(3);
    func_0014fb58(uVar2);
  }
  lVar1 = func_001e4030(4);
  if (lVar1 != 1)
  {
    func_00223758(auStack_170);
  }
  func_001f800c(auStack_170, auStack_30);
  baseelf_6();
  return;
}
