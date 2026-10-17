
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
extern int func_002ffc08();
extern int func_0030c828();
void func_002fb088(int param_1)
{
  int iVar1;
  int iVar2;
  iVar2 = 4;
  func_0030c828(param_1, 0, 0x38);
  iVar1 = param_1;
  do
  {
    iVar2 = iVar2 + (-1);
    func_002ffc08(iVar1);
    iVar1 = 0x20 + iVar1;
  }
  while ((-1) < iVar2);
  func_002ffc08(param_1 + 0xa0);
  *((undefined8 *) (param_1 + 0xc0)) = 0;
  *((undefined4 *) (param_1 + 0xdc)) = 0;
  *((undefined8 *) (param_1 + 200)) = 0;
  *((undefined8 *) (param_1 + 0xd0)) = 0;
 do { *((undefined4 *) (param_1 + 0xd8)) = 0; } while (0);
  return;
}
