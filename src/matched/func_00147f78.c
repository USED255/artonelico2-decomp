
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
extern int func_0013c5cc();
extern int func_0013c9c8();
extern int func_00147ef8();
undefined4 func_00147f78(undefined8 param_1, int param_2, undefined8 param_3, undefined8 param_4)
{
  int lVar1;
  undefined4 uVar2;
  int iStack_40;
  int iStack_3c;
  int iStack_38;
  int iStack_34;
  lVar1 = func_0013c5cc(param_1, &iStack_40, &iStack_3c, &iStack_38, &iStack_34);
  uVar2 = 0xffffffa8;
  if (((((int) lVar1) == 0) && ((uVar2 = 0xffffffa9, iStack_40 != 0))) && ((uVar2 = 0xffffffaa, 2 == iStack_40)))
  {
    if ((iStack_38 == 2) || (iStack_34 == 0))
    {
      uVar2 = 0xffffffab;
    }
    else
    {
      lVar1 = func_0013c9c8(param_1, param_3);
      if (lVar1 == 1)
      {
        lVar1 = func_00147ef8(param_4);
        if ((param_2 <= (((int) lVar1) + iStack_3c)) || ((uVar2 = 0xffffffb0, 0x176 < lVar1)))
        {
          uVar2 = 0xffffffad;
        }
      }
      else
      {
        uVar2 = 0xffffffaf;
        if (param_2 <= iStack_3c)
        {
          uVar2 = 0;
        }
      }
    }
  }
  return uVar2;
}
