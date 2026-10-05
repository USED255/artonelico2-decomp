
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
extern int func_0019e660();
extern int func_0019ea50();
extern int func_00253848();
extern int func_00254378();
void func_00252dd8(int param_1)
{
  undefined8 uVar1;
  long lVar2;
  if ((*((int *) (param_1 + 0x40c))) < 10)
  {
    func_00253848(param_1 + 0x8510, *((undefined4 *) (param_1 + 0x410)));
  }
  else
  {
    func_00254378(param_1 + 0xaeb0, *((undefined4 *) (param_1 + 0x410)));
  }
  uVar1 = func_0019e660(1);
  ;
  if (func_0019ea50(uVar1) != 0)
  {
    *((undefined4 *) (param_1 + 0xb970)) = 1;
  }
  return;
}
