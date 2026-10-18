
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
extern int baseelf_50();
extern int func_0018ff18();
extern int func_0018ff48();
extern int func_00191c24();
extern int func_00193c44();
extern int func_00193d40();
extern int func_002352b4();
extern int func_002451a0();
extern int func_002473cc();
extern volatile unsigned char D_00BB8538;
void func_0025b258(void)
{
  int iVar1;
  int iVar2;
  iVar1 = 0;
  func_00191c24();
  func_00193d40();
  baseelf_50();
  do
  {
    iVar2 = iVar1 * 0xc;
    iVar1 = iVar1 + 1;
    { unsigned char *p = (unsigned char *) (&D_00BB8538) + iVar2; *((undefined4 *) (p + 4)) = 1; }
  }
  while (iVar1 < 3);
  iVar1 = 0;
  do
  {
    iVar2 = iVar1 + 1;
    func_002451a0(iVar1, 0xffffffffffffffff, 1);
    iVar1 = iVar2;
  }
  while (iVar2 < 0xf3);
  iVar1 = 0;
  do
  {
    iVar2 = iVar1 + 1;
    func_002473cc(iVar1, 0xffffffffffffffff, 1);
    iVar1 = iVar2;
  }
  while (iVar2 < 0x51);
  iVar1 = 0;
  func_002352b4();
  func_0018ff48();
  func_0018ff18();
  do
  {
    func_00193c44(iVar1);
    iVar1 = iVar1 + 1;
  }
  while (iVar1 < 0x4d0);
  return;
}
