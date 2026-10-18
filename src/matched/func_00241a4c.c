
typedef unsigned char undefined;
typedef unsigned char undefined1;
typedef unsigned short short;
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
extern char D_009DF368;
extern unsigned int _CONCAT44(unsigned int, unsigned int);
extern unsigned long long _CONCAT82(unsigned int, unsigned int);
extern void SYNC(int);
extern void EI(void);
extern void DI(void);
extern void FlushCache(int);
extern int syscall(int);
extern int func_00144390();
extern int func_00144f50();
extern int func_00145280();
extern int func_00145324();
extern int func_00235ec8();
extern int func_00240740();
extern int func_0024e770();
extern int func_0024e794();
extern int func_002501c0();
extern int func_002501f8();
extern int func_00250470();
extern int func_002504a0();
extern int func_002504dc();
extern int func_002505ec();
extern int func_00250628();
extern int LibcStdio_47();
void func_00241a4c(int param_1)
{
  long lVar1;
  undefined8 uVar2;
  int iVar3;
  int lVar4;
  short *puVar5;
  int iVar6;
  int iVar7;
  short uVar8;
  *((short *) (param_1 + 0x17e2)) = 0;
  lVar4 = 0;
  uVar8 = 0;
  do
  {
    lVar1 = func_0024e770(lVar4);
    if (lVar1 == 1)
    {
      if (lVar4 == (*((short *) (param_1 + 0x7d9c))))
      {
        uVar8 = *((short *) (param_1 + 0x17e2));
      }
      uVar2 = func_00235ec8(lVar4);
      LibcStdio_47((param_1 + ((*((short *) (param_1 + 0x17e2))) * 0x100)) + 0x17e4, 0x100, (&D_009DF368), uVar2);
      func_00240740(param_1, lVar4);
    }
    lVar4 = (long) (((int) lVar4) + 1);
    iVar7 = param_1 + 0x40c;
  }
  while (lVar4 < 100);
  func_00144390(iVar7);
  func_00144f50(iVar7, 0x10, *((short *) (param_1 + 0x17e2)), 2, param_1 + 0x10c8);
  if (0 < (*((short *) (param_1 + 0x17e2))))
  {
    lVar4 = 0;
    puVar5 = (short *) (param_1 + 0x1718);
    iVar3 = param_1 + 0x17e4;
    iVar6 = param_1;
    do
    {
      *((int *) (iVar6 + 0x10cc)) = iVar3;
      *((short *) (iVar6 + 0x10c8)) = 5;
      *((short *) (iVar6 + 0x10ca)) = 3;
      lVar1 = func_0024e794(*puVar5);
      if (lVar1 == 1)
      {
        *((short *) (iVar6 + 0x10d2)) = 0;
        *((short *) (iVar6 + 0x10d0)) = 4;
        *((undefined4 *) (iVar6 + 0x10d4)) = 0;
      }
      else
      {
        *((short *) (iVar6 + 0x10d2)) = 0;
        *((short *) (iVar6 + 0x10d0)) = 4;
        *((undefined4 *) (iVar6 + 0x10d4)) = 0xffffffff;
      }
      lVar4 = (long) (((int) lVar4) + 1);
      puVar5 = puVar5 + 1;
      iVar3 = iVar3 + 0x100;
      iVar6 = iVar6 + 0x10;
    }
    while (lVar4 < (*((short *) (param_1 + 0x17e2))));
  }
  func_00145324(iVar7, 400, 0xfe);
  *((undefined1 *) (param_1 + 0x40e)) = 0x10;
  *((undefined1 *) (param_1 + 0x40d)) = *((undefined1 *) (param_1 + 0x40f));
  iVar6 = param_1 + 0x7d28;
  func_00145280(iVar7, uVar8);
  *((uint *) (param_1 + 0x82c)) = (*((uint *) (param_1 + 0x82c))) & 0xf7ffffff;
  *((short *) (param_1 + 0x7d9e)) = 0xffff;
  func_002501c0(param_1 + 0x7cf0);
  func_002501f8(param_1 + 0x7cf0, 0x140, 0x14);
  func_002505ec(param_1 + 0x7d5c);
  func_00250628(param_1 + 0x7d5c, 0x3c, 0x28);
  func_00250470(iVar6);
  func_002504dc(iVar6);
  func_002504a0(iVar6, 0x14, 0x104);
  return;
}
